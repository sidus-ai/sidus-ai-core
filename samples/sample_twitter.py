#
# An example of using a Twitter connection and publishing a single post.
#
# This example shows how to set up a connection, as well as how to interact with the Twitter API
#

import os
import sidusai

import sidusai.plugins.twitter as twitter

agent = sidusai.Agent()
_ = twitter.TwitterExtensionPlugin(agent)


class Tweet(sidusai.AgentValue):
    def __init__(self):
        super().__init__()

        self.message = ''


@agent.configuration()
def twitter_connection_configuration(props: twitter.TwitterConnectionProperty):
    props.client_id = os.environ['client_id']
    props.client_secret = os.environ['client_secret']

    props.api_key = os.environ['api_key']
    props.api_secret = os.environ['api_secret']

    props.bearer_token = os.environ['bearer_token']

    props.access_token = os.environ['access_token']
    props.access_token_secret = os.environ['access_token_secret']


@agent.skill()
def build_tweet_message(value: Tweet) -> Tweet:
    value.message = 'Hello'
    return value


@agent.task(
    task_name='post_tweet',
    skill_names=['build_tweet_message']
)
class PostTweet(sidusai.AgentTask):

    def __init__(self, connection: twitter.TwitterConnection):
        super().__init__()
        self.conn = connection

    def forward(self, *args, **kwargs) -> sidusai.AgentValue:
        return Tweet()

    def on_complete(self, value: Tweet, **kwargs) -> None:
        self.conn.client.create_tweet(text=value.message)


@agent.loop(fixed_interval_sec=1)
def hello_world_loop():
    task = agent.create_task_from_context(PostTweet)
    agent.task_execute(task)

    agent.halt()


if __name__ == '__main__':
    agent.application_run()
