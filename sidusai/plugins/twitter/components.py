import tweepy


class TwitterClient:

    def __init__(self, bearer_token: str, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self._validate_connection_configuration()

        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )

        auth = tweepy.OAuthHandler(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )

        self.api = tweepy.API(auth)

    def tweet(self, message: str):
        if message is None:
            raise ValueError('Message can not be None')
        self.client.create_tweet(text=message)

    def _validate_connection(self):
        try:
            self.api.verify_credentials()
        except Exception as e:
            raise ConnectionRefusedError(e)

    def _validate_connection_configuration(self):
        unset_parameters = []
        if self.bearer_token is None:
            unset_parameters.append('bearer_token')

        if self.api_key is None:
            unset_parameters.append('api_key')

        if self.api_secret is None:
            unset_parameters.append('api_secret')

        if self.access_token is None:
            unset_parameters.append('access_token')

        if self.access_token_secret is None:
            unset_parameters.append('access_token_secret')

        if len(unset_parameters) > 0:
            raise ValueError(
                f'Invalid Twitter connection configuration. {' '.join(unset_parameters)} parameters are not set'
            )
