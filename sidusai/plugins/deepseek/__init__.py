import sidusai as sai

__required_modules__ = ['requests']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.deepseek.skills as skills
import sidusai.plugins.deepseek.components as components

__deepseek_agent_name__ = 'ds_ai_agent_name'


class DeepSeekPlugin(sai.AgentPlugin):

    def __init__(self, api_key, temperature: float = None, top_p: float = None,
                 max_tokens: float = None, model_name: str = None):
        super().__init__()

        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.model_name = model_name

    def apply_plugin(self, agent: sai.Agent):
        agent.add_component_builder(self._build_deep_seek_connection)

        agent.add_skill(skills.ds_chat_transform_skill)

    def _build_deep_seek_connection(self) -> components.DeepSeekClientComponent:
        return components.DeepSeekClientComponent(
            api_key=self.api_key,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            model_name=self.model_name
        )


class DeepSeekChatTask(sai.CompletedAgentTask):
    pass


class DeepSeekSingleChatAgent(sai.Agent):

    def __init__(self, api_key, system_prompt: str = None, prepare_task_skills: [] = None,
                 temperature: float = None, top_p: float = None,
                 max_tokens: float = None, model_name: str = None):
        super().__init__(__deepseek_agent_name__)

        self.system_prompt = system_prompt
        self.chat = sai.ChatAgentValue([])

        ds_plugin = DeepSeekPlugin(
            api_key=api_key,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            model_name=model_name
        )

        ds_plugin.apply_plugin(self)
        if system_prompt is not None:
            self.chat.append_system(system_prompt)

        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(skills.ds_chat_transform_skill)

        task_skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(DeepSeekChatTask, skill_names=task_skill_names)

    def send_to_chat(self, message: str, handler):
        if message is None:
            raise ValueError('Message can not be None')

        self.chat.append_user(message)
        task = DeepSeekChatTask(self).data(self.chat).then(handler)
        self.task_execute(task)
