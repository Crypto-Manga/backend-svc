import json
from datetime import timedelta
from string import Template
from typing import List

import requests

from cryptomanga.persistence.cache.heroku_redis import HerokuRedis


class TheGraphApi:
    CRYPTOMANGA_QUERY = Template(
        '{ owner(id:"$wallet") { id ownedTokens { id } balance } }'
    )
    CRYPTOMANGA_ENDPOINT = "https://api.thegraph.com/subgraphs/name/adijo/crypto-manga"

    WORKSHOP_QUERY = Template(
        '{ owner(id:"$wallet") { id ownedTokens { id } balance } }'
    )
    WORKSHOP_ENDPOINT = "https://api.thegraph.com/subgraphs/name/adijo/workshop"

    def __init__(self, redis: HerokuRedis) -> None:
        self.redis = redis

    def get_cma_tokens_for_wallet(self, wallet: str) -> List[int]:
        print(wallet)
        return self._get_tokens(
            wallet,
            TheGraphApi.CRYPTOMANGA_ENDPOINT,
            TheGraphApi.CRYPTOMANGA_QUERY.substitute(wallet=wallet),
            "cma",
        )

    def get_workshop_tokens_for_wallet(self, wallet: str) -> List[int]:
        return self._get_tokens(
            wallet,
            TheGraphApi.WORKSHOP_ENDPOINT,
            TheGraphApi.WORKSHOP_QUERY.substitute(wallet=wallet),
            "workshop",
        )

    def _get_tokens(self, wallet: str, endpoint: str, query: str, prefix: str):
        if self.redis.exists(f"{prefix}:{wallet}"):
            return json.loads(self.redis.get(f"{prefix}:{wallet}"))

        resp = requests.post(
            endpoint,
            json={"query": query},
        )

        if resp.status_code != 200:
            raise Exception("Failed to fetch tokens")

        data = resp.json()
        if data["data"]["owner"] is None:  # no tokens belong to this wallet
            return list()

        tokens = [
            int(token["id"], 16)  # hex -> int
            for token in data["data"]["owner"]["ownedTokens"]
        ]
        self.redis.set(
            key=f"{prefix}:{wallet}", value=json.dumps(tokens), time=timedelta(hours=1)
        )
        return tokens
