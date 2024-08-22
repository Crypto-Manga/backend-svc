import os

import tweepy


class TwitterApi:
    RATE_CTR_KEY = "ctr"
    RATE_LIMIT = 200  # 200 status updates per 15 min window

    def __init__(self, redis) -> None:
        auth = tweepy.OAuthHandler(
            os.environ["twitter_api_key"], os.environ["twitter_key_secret"]
        )
        auth.set_access_token(
            os.environ["twitter_access_token"], os.environ["twitter_token_secret"]
        )

        self.api = tweepy.API(auth, retry_count=2, retry_delay=0.5)
        self.redis = redis

    def execute(self, handle: str, text: str, in_reply_to_status_id: int, media_ids=[]):
        if handle != "TomoBotz":

            should_tweet = self.redis.get(TwitterApi.RATE_CTR_KEY) is None or (
                int(self.redis.get(TwitterApi.RATE_CTR_KEY)) <= TwitterApi.RATE_LIMIT
            )
            if should_tweet:

                self.api.update_status(
                    f"{text}",
                    in_reply_to_status_id=in_reply_to_status_id,
                    media_ids=media_ids,
                    auto_populate_reply_metadata=True,
                )

                self.redis.incr(TwitterApi.RATE_CTR_KEY)
