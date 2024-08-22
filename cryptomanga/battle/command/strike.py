from typing import Optional

from cryptomanga.battle.command.base import BaseCommand
from cryptomanga.battle.response.twitter_response import get_response
from cryptomanga.battle.state import BattleState
from cryptomanga.handler.sampling import normal


class Strike(BaseCommand):

    SPECIAL_ITEMS = {
        "fanny-pack": 10,
        "choker-light": 20,
        "shurinken": 35,
        "ring": 55,
        "blaster": 80,
        "power-glove": 110,
        "aureum-yukata": 125,
        "polymer-yukata": 90,
    }

    SPECIAL_ITEMS_TEXT = {
        "shurinken": "Your shuriken added stinging kick to your strike!",
        "aureum-yukata": "You channeled the powers of your Aureum Yukata to blow your opponent away!",
        "polymer-yukata": "Your d3o Yukata supercharged your strike!",
        "power-glove": "Your powerglove's helix beams added serious bite to your strike!",
        "ring": "Your ring stunned @user2 along with the strike!",
        "choker-light": "Your light blinded the opponent & enhanced your strike!",
        "ring": "Your ring stunned the opponent along with the strike!",
        "blaster": "Your blaster's protonfire added extra power to your strike!",
    }

    def _calculate_strike_hp(self, combat: int, special_item: Optional[str] = None):

        battle_combat = combat + Strike.SPECIAL_ITEMS.get(special_item, 0)
        print(battle_combat)

        if battle_combat <= 100:
            return normal(20, 2)
        elif 100 < battle_combat <= 150:
            return normal(25, 3)
        elif 150 < battle_combat <= 200:
            return normal(30, 3)
        else:
            return normal(40, 3)

    def _get_special_item(self, text: str) -> Optional[str]:
        for key in Strike.SPECIAL_ITEMS.keys():
            if text.find(key) > -1:
                return key

    def execute(self, text: str, handle: str, status_id: int) -> BattleState:

        key = self.redis.get(handle)
        if key is None:
            return

        battle: BattleState = BattleState.deserialize(self.redis.get(key))

        if battle.get_current_player() != handle:
            return

        metadata = self._get_current_player_metadata(battle)
        body = metadata.get_attribute("Body")

        combat = int(metadata.get_attribute("Combat"))
        special_item = self._get_special_item(text)

        print("special item", special_item)

        battle.process_strike(
            self._calculate_strike_hp(combat, special_item=special_item)
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
            response = get_response("!strike", body_type=body).format(
                p1=battle.p1_shell,
                p2=battle.p2_shell,
                p1_health=int(battle.p1_health),
                p2_health=int(battle.p2_health),
                special_item_text=Strike.SPECIAL_ITEMS_TEXT.get(special_item)
                if special_item
                else "",
                p1_arrow="⬇️"
                if battle.get_current_player_idx() == BattleState.P2
                else "",
                p2_arrow="⬇️"
                if battle.get_current_player_idx() == BattleState.P1
                else "",
            )

            self.twitter.execute(handle, response, status_id)

            battle.turns += 1
            self.redis.set(key, battle.serialize())
