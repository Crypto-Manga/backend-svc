import requests

from cryptomanga.handler.the_graph_api import TheGraphApi
from cryptomanga.persistence.cache.heroku_redis import HerokuRedis


class WorkshopApi:

    ENDPOINT = "https://workshop-service.herokuapp.com/metadata/{id}.json"

    def __init__(self, redis: HerokuRedis, graph: TheGraphApi):
        self.redis = redis
        self.graph = graph

    def does_wallet_own_asset(self, wallet: str, item: str) -> bool:
        key = f"{wallet}:{item}"

        if self.redis.exists(key):
            return bool(self.redis.get(key))

        tokens = self.graph.get_workshop_tokens_for_wallet(wallet.lower())
        is_owned = False
        for token in tokens:
            if self._does_id_match_item(token, item):
                is_owned = True
                break

        self.redis.set(key=key, value=str(is_owned))
        return is_owned

    def _does_id_match_item(self, id: int, item: str) -> bool:

        resp = requests.get(WorkshopApi.ENDPOINT.format(id=id))
        if resp.status_code != 200:
            raise Exception("Failed to fetch tokens from workshop")

        workshop_item = resp.json()["name"]

        if workshop_item.startswith(item):
            return True

        return False
