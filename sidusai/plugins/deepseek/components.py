import requests
import json

from sidusai.core.plugin import ChatAgentValue

__default_utl__ = 'https://api.deepseek.com/chat/completions'

# Default text generation params
__default_deepseek_model__ = 'deepseek-chat'
__default_max_tokens__ = 1024
__default_temperature__ = 0.9
__default_top_p__ = 1
__frequency_penalty__ = 0
__presence_penalty__ = 0


class DeepSeekResponse:

    def __init__(self, response: requests.Response):
        obj = json.loads(response.text)

        self.status_code = response.status_code
        # Convert JSON to object
        self.id = obj['id'] if 'id' in obj else None
        self.object = obj['object'] if 'object' in obj else None
        self.created = obj['created'] if 'created' in obj else None
        self.model = obj['model'] if 'model' in obj else None
        self.system_fingerprint = obj['system_fingerprint'] if 'system_fingerprint' in obj else None

        if 'usage' in obj:
            usage = obj['usage']
            self.prompt_tokens = usage['prompt_tokens'] \
                if 'prompt_tokens' in usage else None
            self.completion_tokens = usage['completion_tokens'] \
                if 'completion_tokens' in usage else None
            self.total_tokens = usage['total_tokens'] \
                if 'total_tokens' in usage else None
            self.prompt_cache_hit_tokens = usage['prompt_cache_hit_tokens'] \
                if 'prompt_cache_hit_tokens' in usage else None
            self.prompt_cache_miss_tokens = usage['prompt_cache_miss_tokens'] \
                if 'prompt_cache_miss_tokens' in usage else None

        self.choices = []
        self.messages = []
        self.last_message = None

        if 'choices' in obj:
            choices = obj['choices']
            self.choices = choices
            self.messages = []
            for choice in choices:
                self.messages.append(choice['message'])

            message_len = len(self.messages)
            if message_len > 0:
                self.last_message = self.messages[message_len - 1]


class DeepSeekClientComponent:
    """
    A class-component that wraps data and connection information. It is used for
    formation and subsequent use in the context of the application core.
    """

    params: dict = {}

    def __init__(self, api_key: str, model_name: str = None, **kwargs):
        self.api_key = api_key

        self.model_name = model_name if model_name is not None else __default_deepseek_model__
        self.params = kwargs

    def request(self, chat: ChatAgentValue) -> DeepSeekResponse:
        payload = json.dumps(self._build_payload(chat))
        headers = self._build_headers()

        response = requests.request('POST', __default_utl__, headers=headers, data=payload)
        return DeepSeekResponse(response)

    def _build_payload(self, chat: ChatAgentValue):
        # TODO: Expand the configurability of the request

        messages = [{'role': v['role'], 'content': v['content']} for v in chat.messages]
        default_payload = {
            "messages": messages,
            "model": self.model_name,
            "frequency_penalty": __frequency_penalty__,
            "max_tokens": __default_max_tokens__,
            "presence_penalty": __presence_penalty__,
            "response_format": {
                "type": "text"
            },
            "stop": None,
            "stream": False,
            "stream_options": None,
            "temperature": __default_temperature__,
            "top_p": __default_top_p__,
            "tools": None,
            "tool_choice": "none",
            "logprobs": False,
            "top_logprobs": None
        }

        return_payload = dict()

        for key in default_payload:
            if key in self.params:
                return_payload.update({
                    key: self.params[key]
                })
            else:
                return_payload.update({
                    key: default_payload[key]
                })

        return return_payload

    def _build_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
