import re

from cryptomanga.battle.command.base import BaseCommand
from cryptomanga.battle.state import BattleState


class Duel(BaseCommand):

    NO_SHELLS_TEXT = """Hey there, nomad! You must own + register a shell to compete in the DarkBattle.

1. Obtain a shell: opensea.io/collection/cryptomanga-genesis
2. Register your shell: cryptomanga.club/academy 
3. Return here to to duel!

Without a response, this duel will time out in 24 hours."""

    def execute(self, text: str, p1: str, status_id: int):
        p1_shell = int(re.findall(r"#[^\s.]*", text)[0].replace("#", ""))

        if self.redis.get(p1) is not None:
            return

        shells = self._get_shells(p1)

        if p1_shell not in shells:
            self.twitter.execute(
                p1, Duel.NO_SHELLS_TEXT, in_reply_to_status_id=status_id
            )
            return

        p2: str = re.findall(r"@[^\s.]*", text)[0].replace("@", "")

        if p1 == p2:
            return

        key: str = self._construct_redis_key(p1, p2)

        battle: BattleState = BattleState.init(p1=p1, p2=p2, p1_shell=p1_shell)

        self.redis.set(p2, key)
        self.redis.set(p1, key)
        self.redis.set(key, battle.serialize())
