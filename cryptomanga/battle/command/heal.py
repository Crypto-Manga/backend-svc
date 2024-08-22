from typing import Optional

from cryptomanga.battle.command.base import BaseCommand
from cryptomanga.battle.response.twitter_response import get_response
from cryptomanga.battle.state import BattleState
from cryptomanga.handler.sampling import normal
from cryptomanga.persistence.model import Metadata


class Heal(BaseCommand):
    SPECIAL_ITEMS_TEXT = {
        "aureum-yukata": "Your Aureum Yukata enhanced your heal!",
        "polymer-yukata": "Your Polymer Yukata enhanced your heal!",
    }

    def _calculate_heal_hp(self, skill: int, special_item=None):

        if special_item == "aureum-yukata":
            skill += 70
        elif special_item == "polymer-yukata":
            skill += 30

        if skill <= 100:
            return normal(15, 2)
        elif 100 < skill <= 150:
            return normal(20, 3)
        elif 150 < skill <= 200:
            return normal(25, 3)
        else:
            return normal(30, 3)

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

        if not battle.can_heal():
            return

        metadata = self._get_current_player_metadata(battle)
        skill = int(metadata.get_attribute("Skill"))

        special_item = self._get_special_item(handle)
        print(special_item)

        battle.increase_health(
            self._calculate_heal_hp(skill, special_item=special_item)
        )

        body = metadata.get_attribute("Body")

        response = get_response("!heal", body_type=body).format(
            p1=battle.p1_shell,
            p2=battle.p2_shell,
            p1_health=int(battle.p1_health),
            p2_health=int(battle.p2_health),
            special_item_text=Heal.SPECIAL_ITEMS_TEXT.get(special_item)
            if special_item
            else "",
            p1_arrow="⬆️ " if battle.get_current_player_idx() == BattleState.P1 else "",
            p2_arrow="⬆️ " if battle.get_current_player_idx() == BattleState.P2 else "",
        )

        self.twitter.execute(handle, response, status_id)

        battle.turns += 1
        self.redis.set(key, battle.serialize())

    def _is_authorized(self, text: str, handle: str) -> bool:
        return True
