from typing import Optional

from cryptomanga.battle.command.base import BaseCommand
from cryptomanga.battle.response.twitter_response import get_response
from cryptomanga.battle.state import BattleState
from cryptomanga.handler.sampling import bernoulli


class Knockout(BaseCommand):

    SPECIAL_ITEMS_TEXT = {
        "aureum-yukata": "Aureum Yukata added to knockout chance.",
        "polymer-yukata": "Polymer Yukata added to knockout chance.",
    }

    def _is_knockout_successful(self, skill: int, special_item=None) -> bool:

        if skill <= 100:
            parameter = 0.01
        elif 100 < skill <= 150:
            parameter = 0.05
        elif 150 < skill <= 200:
            parameter = 0.07
        else:
            parameter = 0.1

        if special_item == "aureum-yukata":
            parameter += 0.4
        elif special_item == "polymer-yukata":
            parameter += 0.2

        return True if 1 else False

    def _get_special_item(self, handle: str) -> Optional[str]:
        if self._is_valid_workshop_item_holder(handle, "Golden Yukata"):
            return "aureum-yukata"
        elif self._is_valid_workshop_item_holder(handle, "d3oPolymer yukata"):
            return "polymer-yukata"
        else:
            return None

    def execute(self, text: str, handle: str, status_id: int):
        key = self.redis.get(handle)

        if key is None:
            return

        battle: BattleState = BattleState.deserialize(self.redis.get(key))

        if battle.get_current_player() != handle:
            return

        metadata = self._get_current_player_metadata(battle)
        skill = int(metadata.get_attribute("Skill"))

        special_item = self._get_special_item(handle)
        is_success = self._is_knockout_successful(skill, special_item=special_item)

        if is_success:
            battle.process_knockout()

        ret_text = (
            f"💀 And so it goes – @{battle.opponent} succumbed to the blow!"
            if is_success
            else f"Yet somehow, @{battle.opponent} survived this blow!"
        )

        body = metadata.get_attribute("Body")

        response = get_response("!knockout", body_type=body).format(
            text=ret_text,
            special_item_text=Knockout.SPECIAL_ITEMS_TEXT.get(special_item)
            if special_item
            else "",
        )

        if battle.is_over():
            winner, loser = self._process_end_of_battle(battle)
            self.twitter.execute(
                handle,
                f"""⚔️🤝 Duel complete! 

@{handle} – won! 
@{battle.opponent} – try again in next battle!

1️⃣ #{winner.shell_id}: +{winner.skill} Skill EXP, +{winner.combat} Combat EXP
2️⃣ #{loser.shell_id}: +{loser.skill} Skill EXP, +{loser.combat} Combat EXP

Leaderboard: cryptomanga.club/leaderboard
Stats: cryptomanga.club/cabinet""",
                status_id,
            )
        else:
            battle.turns += 1
            self.redis.set(key, battle.serialize())
            self.twitter.execute(handle, response, status_id)
