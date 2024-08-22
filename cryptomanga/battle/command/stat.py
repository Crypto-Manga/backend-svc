from click import BaseCommand

from cryptomanga.battle.state import BattleState


class Stat(BaseCommand):
    def execute(self, text: str, handle: str, status_id: int):
        key = self.redis.get(handle)

        if key is None:
            return

        battle: BattleState = BattleState.deserialize(self.redis.get(key))
