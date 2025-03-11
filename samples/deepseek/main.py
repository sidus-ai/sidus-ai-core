import os
import sidusai as sai
import sidusai.plugins.deepseek as ds

deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
system_prompt = 'You are a helpful assistant'

agent = ds.DeepSeekSingleChatAgent(
    api_key=deepseek_api_key,
    system_prompt=system_prompt,
)


def accept_response(value: sai.ChatAgentValue):
    message = value.last_content()
    print(f'Assistant: \n{message}')


if __name__ == '__main__':
    agent.application_build()
    agent.send_to_chat(
        message='What is the capital of China?',
        handler=accept_response
    )
