import datetime
import random
import re
from dataclasses import dataclass
from typing import Dict

from cryptomanga.battle.command.accept import Accept
from cryptomanga.battle.command.duel import Duel
from cryptomanga.battle.command.heal import Heal
from cryptomanga.battle.command.knockout import Knockout
from cryptomanga.battle.command.strike import Strike
from cryptomanga.battle.state import BattleState
from cryptomanga.battle.workshop import WorkshopApi
from cryptomanga.handler.base import BaseHandler
from cryptomanga.handler.mongo_api import MongoApi
from cryptomanga.handler.the_graph_api import TheGraphApi
from cryptomanga.handler.twitter_api import TwitterApi
from cryptomanga.persistence.cache.heroku_redis import HerokuRedis
from cryptomanga.persistence.model import Metadata


class BattleHandler(BaseHandler):
    def __init__(
        self,
        redis: HerokuRedis,
        twitter: TwitterApi,
        mongo: MongoApi,
        graph: TheGraphApi,
        workshop: WorkshopApi,
    ):
        self.redis = redis
        self.twitter = twitter
        self.mongo = mongo
        self.graph = graph
        self.workshop = workshop

    def _extract_text(self, data: Dict) -> str:
        return (
            data["tweet_create_events"][0]["text"]
            .replace("@CryptoMangaNFT", "")
            .replace("@TomoBotz", "")
            .strip()
        )

    def handle(self, data: Dict):
        handle: str = data["tweet_create_events"][0]["user"]["screen_name"]
        text: str = self._extract_text(data)
        status_id = data["tweet_create_events"][0]["id"]

        if text.startswith("!duel"):
            Duel(
                redis=self.redis,
                mongo=self.mongo,
                graph=self.graph,
                twitter=self.twitter,
                workshop=self.workshop,
            ).execute(text, handle, status_id)

        else:

            text = re.sub(r"@[^\s.]*", "", text).strip()
            if text.startswith("!accept"):
                Accept(
                    redis=self.redis,
                    mongo=self.mongo,
                    graph=self.graph,
                    twitter=self.twitter,
                    workshop=self.workshop,
                ).execute(text, handle, status_id)

            else:
                if text.startswith("!strike"):
                    Strike(
                        redis=self.redis,
                        mongo=self.mongo,
                        graph=self.graph,
                        twitter=self.twitter,
                        workshop=self.workshop,
                    ).execute(text, handle, status_id)

                elif text.startswith("!knockout"):
                    Knockout(
                        redis=self.redis,
                        mongo=self.mongo,
                        graph=self.graph,
                        twitter=self.twitter,
                        workshop=self.workshop,
                    ).execute(text, handle, status_id)

                elif text.startswith("!heal"):
                    Heal(
                        redis=self.redis,
                        mongo=self.mongo,
                        graph=self.graph,
                        twitter=self.twitter,
                        workshop=self.workshop,
                    ).execute(text, handle, status_id)
