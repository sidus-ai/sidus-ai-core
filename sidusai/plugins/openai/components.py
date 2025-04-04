import sidusai as sai
import openai as ai

model_gpt_4o_mini = 'gpt-4o-mini'
model_gpt_4o = 'gpt-4o'

__default_model_name__ = model_gpt_4o_mini
__default_max_tokens__ = 1024
__default_temperature__ = 0.9
__default_top_p__ = 1
__frequency_penalty__ = 0
__presence_penalty__ = 0


class OpenAiConnector:

    def __init__(self, api_key: str, model_name: str = None):
        self.api_key = api_key
        self.model_name = model_name if model_name is not None else __default_model_name__

        self.client = ai.OpenAI(api_key=self.api_key)

    def request(self, chat: sai.ChatAgentValue) -> ai.ChatCompletion:
        messages = [{'role': v['role'], 'content': v['content']} for v in chat.messages]

        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=__default_temperature__,
            max_tokens=__default_max_tokens__,
            top_p=__default_top_p__,
            frequency_penalty=__frequency_penalty__,
            presence_penalty=__presence_penalty__,
        )
