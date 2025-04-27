import sidusai as sai
# import sidusai.core.plugin as _cp
# import sidusai.plugins.openai.skills as skills
# import sidusai.plugins.openai.components as components

__required_modules__ = ['openai']
sai.utils.validate_modules(__required_modules__)


class OpenAiPlugin(sai.AgentPlugin):

    def __init__(self, api_key: str):
        super().__init__()

        self.api_key = api_key


class OpenAiChatTask(sai.CompletedAgentTask):
    pass


class OpenAIAgent(sai.Agent):
    pass
