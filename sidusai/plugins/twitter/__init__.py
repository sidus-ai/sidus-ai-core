import sidusai

__required_modules__ = ['tweepy']
sidusai.utils.validate_modules(__required_modules__)

import tweepy


class TwitterConnectionProperty:
    """
    Object wrapper for the Twitter agent extension configuration
    """

    def __init__(self, bearer_token, api_key, api_secret, access_token, access_token_secret):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret


class TwitterConnection:
    """
    The object of the formed connection to the Twitter API
    """

    def __init__(self):
        self.client = None
        self.api = None


class TwitterExtensionPlugin(sidusai.AgentExtension):
    """
    Agent extensions with connection to Twitter API.
    Extends the context by adding connection components
    """

    def __init__(self,
                 agent: sidusai.Agent,
                 bearer_token=None,
                 api_key=None,
                 api_secret=None,
                 access_token=None,
                 access_token_secret=None
                 ):
        super().__init__(agent)

        # Connection properties
        self.connection_property = TwitterConnectionProperty(
            bearer_token, api_key, api_secret, access_token, access_token_secret
        )
        self.connection = TwitterConnection()

        # Agent environment
        self.agent.add_component_builder(self.twitter_connection_property_component)
        self.agent.add_component_builder(self.twitter_connection_component)
        self.agent.add_post_processor(twitter_connection_post_processor)

    def twitter_connection_property_component(self) -> TwitterConnectionProperty:
        return self.connection_property

    def twitter_connection_component(self) -> TwitterConnection:
        return self.connection


def twitter_connection_post_processor(props: TwitterConnectionProperty, conn: TwitterConnection):
    _validate_configuration_connection(props)

    conn.client = tweepy.Client(
        bearer_token=props.bearer_token,
        consumer_key=props.api_key,
        consumer_secret=props.api_secret,
        access_token=props.access_token,
        access_token_secret=props.access_token_secret
    )

    auth = tweepy.OAuthHandler(
        consumer_key=props.api_key,
        consumer_secret=props.api_secret,
        access_token=props.access_token,
        access_token_secret=props.access_token_secret
    )

    conn.api = tweepy.API(auth)
    _validate_connection(conn)


def _validate_connection(conn: TwitterConnection):
    try:
        conn.api.verify_credentials()
    except Exception as e:
        raise ConnectionRefusedError(e)


def _validate_configuration_connection(props: TwitterConnectionProperty):
    if props.bearer_token is None:
        raise ValueError('Twitter Bearer key is not found. Please configuration plugin')

    if props.api_key is None:
        raise ValueError('Twitter Consumer API Key is not found. Please configuration plugin')

    if props.api_secret is None:
        raise ValueError('Twitter Consumer API Secret is not found. Please configuration plugin')

    if props.access_token is None:
        raise ValueError('Twitter Access token is not found. Please configuration plugin')

    if props.access_token_secret is None:
        raise ValueError('Twitter Access token secret is not found. Please configuration plugin')
