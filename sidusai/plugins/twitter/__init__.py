import sidusai as sai
import sidusai.core.plugin as _cp
import sidusai.plugins.twitter.components as components
import sidusai.plugins.deepseek as _ds

__required_modules__ = ['tweepy']
sai.utils.validate_modules(__required_modules__)

__default_agent_name__ = 'x_ai_agent_name'


class TwitterPrepareTweetTask(sai.CompletedAgentTask):
    pass


class TwitterAget(sai.Agent):
    def __init__(
        self, system_prompt: str,
        bearer_token: str,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        # [sai.AgentPlugin]
        plugins: list,
        prepare_task_skills: list = None
    ):
        super().__init__(__default_agent_name__)

        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        for plugin in plugins:
            plugin.apply_plugin(self)

        self.add_component_builder(self._build_twitter_client)
        task_skills = prepare_task_skills if prepare_task_skills is not None else []
        task_skills.append(_ds.skills.ds_chat_transform_skill)

        skill_names = _cp.build_and_register_task_skill_names(task_skills, self)
        self.task_registration(TwitterPrepareTweetTask, skill_names=skill_names)

        self.chat = sai.ChatAgentValue([])
        if system_prompt is not None:
            self.chat.append_system(system_prompt)

    def prepare_tweet(self, message: str, handler):
        if message is None:
            raise ValueError('Message can not be None')
        self.chat.append_user(message)

        task = TwitterPrepareTweetTask(self).data(self.chat).then(handler)
        self.task_execute(task)

    def _build_twitter_client(self) -> components.TwitterClient:
        return components.TwitterClient(
            bearer_token=self.bearer_token,
            api_key=self.api_key,
            api_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
