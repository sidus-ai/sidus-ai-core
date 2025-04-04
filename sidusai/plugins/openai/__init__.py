import sidusai as sai

__required_modules__ = ['openai']
sai.utils.validate_modules(__required_modules__)

import sidusai.core.plugin as _cp
import sidusai.plugins.openai.skills as skills
import sidusai.plugins.openai.components as components


class OpenAiPlugin(sai.AgentPlugin):

    def __init__(self, api_key: str):
        super().__init__()

        self.api_key = api_key


class OpenAiChatTask(sai.CompletedAgentTask):
    pass


class OpenAIAgent(sai.Agent):
    pass
