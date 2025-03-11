from sidusai.core.plugin import ChatAgentValue
from sidusai.plugins.deepseek.components import DeepSeekClientComponent


def ds_chat_transform_skill(value: ChatAgentValue, client: DeepSeekClientComponent) -> ChatAgentValue:
    # TODO: Add general response processing to generate a messages stream

    response = client.request(value)
    if response.last_message is not None and 'content' in response.last_message:
        content = response.last_message['content']
        value.append_assistant(content)

    return value
