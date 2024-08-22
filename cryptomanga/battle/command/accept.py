import io
import os
import re

import requests

from cryptomanga.battle.command.base import BaseCommand
from cryptomanga.battle.state import BattleState
from cryptomanga.persistence.model import Metadata


class Accept(BaseCommand):
    def get_images(self, battle: BattleState):
        def _construct_url(ipfs: str) -> str:
            return f"https://cryptomanga.mypinata.cloud/ipfs/{ipfs[7:]}"

        p1, p2 = self._get_metadata(battle)
        url_1, url_2 = _construct_url(p1.image), _construct_url(p2.image)

        image_one = io.BytesIO(requests.get(url_1).content)
        image_two = io.BytesIO(requests.get(url_2).content)

        resp_1 = self.twitter.api.media_upload(filename=p1.image, file=image_one)
        resp_2 = self.twitter.api.media_upload(filename=p2.image, file=image_two)
        return resp_1.media_id, resp_2.media_id

    def _construct_stats_tweet(self, battle: BattleState) -> str:
        p1, p2 = self._get_metadata(battle)
        return f"""🎒✨ Inventory
Player 1: Shell #{battle.p1_shell}
{p1.get_attribute("Skill")} Skill EXP
{p1.get_attribute("Combat")} Combat EXP

Player 2: Shell #{battle.p2_shell}
{p2.get_attribute("Skill")} Skill EXP
{p2.get_attribute("Combat")} Combat EXP"""

    def execute(self, text: str, handle: str, status_id: int):
        p2_shell = int(re.findall(r"#[^\s.]*", text)[0].replace("#", ""))

        if not self._is_authorized(handle, p2_shell):
            return

        key = self.redis.get(handle)

        if key is None:
            return

        battle: BattleState = BattleState.deserialize(self.redis.get(key))

        battle.accept(p2_shell)

        response_text = f"""⚔️🛡️ Duel accepted! Engage your opponent by responding with !strike or !knockout. You have 2 chances to !heal. Special items will enhance power and both shells start with 100 HP.

Commands: faq.cryptomanga.club 

@{battle.get_current_player()}, it's your move!

#darkbattlenft
"""
        img_one, img_two = self.get_images(battle)
        self.twitter.execute(
            handle,
            response_text,
            status_id,
            media_ids=[img_one, img_two],
        )

        self.twitter.execute(handle, self._construct_stats_tweet(battle), status_id)

        self.redis.set(key, battle.serialize())

    def _is_authorized(self, p2: str, p2_shell: int) -> bool:

        if not self.redis.get(p2):
            return False

        shells = self._get_shells(p2)

        if p2_shell not in shells:
            return False

        return True
