import sidusai as sai

__required_modules__ = ['telebot']
sai.utils.validate_modules(__required_modules__)

import telebot as tg
import sidusai.core.plugin as _cp

import sidusai.plugins.telegram.components as components
import sidusai.plugins.deepseek as _ds

__default_tg_agent_name__ = 'tg_ai_agent_name'
__default_parse_mode__ = 'Markdown'

# TODO: Move to agent constructor
__default_tg_timeout__ = 30
__default_tg_interval__ = 1
__default_message_store_limit__ = 100


class TelegramChatAgentValue(sai.ChatAgentValue):
    """
    A wrapper for a transformable chat, enhanced with additional chat management information.
    Includes a temporary progress message, as well as the user ID used to send the response.
    """

    def __init__(self, messages, user_id, removed_message):
        super().__init__(messages)
        self.user_id = user_id
        self.removed_message = removed_message


class TelegramUserRequestTransformTask(sai.CompletedAgentTask):
    pass


class TelegramRequest:
    """
    An auxiliary Telegram response wrapper containing the basic text data of the request,
    including the necessary identifiers and the text of the user's message
    """

    def __init__(self, message):
        _from_user = message.from_user

        self.text = str(message.text).strip()
        self.user_id = _from_user.id
        self.username = _from_user.username
        self.full_name = _from_user.full_name
        self.lang = _from_user.language_code


class TelegramAiAgent(sai.Agent):
    """
    The basic agent of the Telegram bot, which implements the logic of task formation based on the specified skills.
    Telegram event interceptors are implemented in user code.

    The agent also stores the history of user chats (implemented in RAM),
    which allows you to save the context and conduct a conversation with the bot user.

    TODO: Extract client connection
    """

    def __init__(self, bot_api_key: str, system_prompt: str, plugins: [sai.AgentPlugin],
                 prepare_task_skills: [] = None):
        super().__init__(__default_tg_agent_name__)

        self.api_key = bot_api_key
        self.system_prompt = system_prompt
        self.bot = tg.TeleBot(self.api_key, parse_mode=__default_parse_mode__)

        for plugin in plugins:
            plugin.apply_plugin(self)

        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(_ds.skills.ds_chat_transform_skill)

        skill_names = _cp.build_and_register_task_skill_names(task_skills, self)

        self.add_loop_method(self._tg_pooling_loop, __default_tg_interval__)
        self.task_registration(TelegramUserRequestTransformTask, skill_names=skill_names)

        # TODO: Move to wrapper to solve thread race problem
        self.cache = components.TelegramChatInMemoryCache(__default_message_store_limit__)

    def send_answer(self, tg_request: TelegramRequest):
        user_id = tg_request.user_id
        lock = self.cache.is_locking(user_id)
        if lock:
            self.bot.send_message(user_id, 'You have already sent a request. Expect a response')
            return

        self._set_prompt_if_cache_not_exist(user_id)
        self.cache.put_user(user_id, tg_request.text)
        chat_messages = self.cache[user_id]

        removed = self.bot.send_message(user_id, 'processing...')
        chat = TelegramChatAgentValue(chat_messages, user_id, removed)
        task = TelegramUserRequestTransformTask(self).data(chat).then(self._on_complete_task)
        self.cache.lock(user_id)
        self.task_execute(task)

    def _on_complete_task(self, chat: TelegramChatAgentValue):
        self.cache.unlock(chat.user_id)
        if chat.removed_message is not None:
            self.bot.delete_message(chat.removed_message.chat.id, chat.removed_message.id)

        msg = chat.last_content()
        msg = msg if msg is not None else 'Content is empty. Please check code.'
        self.bot.send_message(chat.user_id, msg)

    def _set_prompt_if_cache_not_exist(self, user_id):
        chat_messages = self.cache[user_id]
        if chat_messages is None:
            self.cache.put_system(user_id=user_id, content=self.system_prompt)

    def _tg_pooling_loop(self):
        offset = self.bot.last_update_id + 1
        res = self.bot.get_updates(offset=offset, timeout=__default_tg_timeout__)
        self.bot.process_new_updates(res)
