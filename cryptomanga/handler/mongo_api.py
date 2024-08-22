import itertools
from typing import List


class MongoApi:
    def __init__(self, mongo) -> None:
        self.mongo = mongo

    def get_wallets(self, handle: str) -> List[str]:
        response = self.mongo.db.academy.find_one({"handle": handle})
        return response["wallets"] if response else list()

    def get_all_wallets(self) -> List[str]:
        response = self.mongo.db.academy.find({})
        return list(itertools.chain(*[x["wallets"] for x in response]))
