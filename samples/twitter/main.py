import os
import sidusai as sai
import sidusai.plugins.deepseek as ds
import sidusai.plugins.twitter as x

deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')

client_id = os.environ['X_CLIENT_ID']
client_secret = os.environ['X_CLIENT_SECRET']
api_key = os.environ['X_API_KEY']
api_secret = os.environ['X_API_SECRET']
bearer_token = os.environ['X_BEARER_TOKEN']
access_token = os.environ['X_ACCESS_TOKEN']
access_token_secret = os.environ['X_ACCESS_TOKEN_SECRET']

system_prompt = 'You are a very helpful assistant. You answer briefly.'

deepseek_plugin = ds.DeepSeekPlugin(
    api_key=deepseek_api_key,
    temperature=0.1
)

agent = x.TwitterAget(
    system_prompt=system_prompt,
    bearer_token=bearer_token,
    api_key=api_key,
    api_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    plugins=[deepseek_plugin]
)


def post_tweet(chat: sai.ChatAgentValue, connection: x.components.TwitterClient):
    message = chat.last_content()
    if message is None:
        raise ValueError('Message can not be None')
    connection.tweet(message)


if __name__ == '__main__':
    agent.application_build()
    agent.prepare_tweet('What is the capital of China?', post_tweet)
