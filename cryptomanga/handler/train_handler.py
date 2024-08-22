import datetime
import random
from typing import Dict, List

from cryptomanga import db
from cryptomanga.handler.base import BaseHandler
from cryptomanga.handler.commands import Command
from cryptomanga.handler.enums import GameOutcome
from cryptomanga.handler.mongo_api import MongoApi
from cryptomanga.handler.response_dispatch import ResponseDispatch
from cryptomanga.handler.sampling import bernoulli, normal
from cryptomanga.handler.the_graph_api import TheGraphApi
from cryptomanga.handler.twitter_api import TwitterApi
from cryptomanga.persistence.model import Attribute, Metadata, Training


class TrainHandler(BaseHandler):
    def __init__(
        self, twitter: TwitterApi, graph: TheGraphApi, mongo: MongoApi
    ) -> None:
        self.twitter = twitter
        self.graph = graph
        self.mongo = mongo

    def _extract_handle(self, data: Dict) -> str:
        return data["tweet_create_events"][0]["user"]["screen_name"]

    def _sanitize_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("@CryptoMangaBot"):
            bot, cmd, choice = text.split()
            text = f"{cmd} {choice} {bot}"
            return text
        return text

    def _extract_command(self, text: str) -> str:
        if text.startswith("!evade") or text.startswith("!mentor"):
            return "train"
        else:
            raise

    def _extract_text(self, data: Dict) -> str:
        return (
            data["tweet_create_events"][0]["text"]
            .replace("@CryptoMangaNFT", "")
            .strip()
        )

    def _shells_for_wallet(self, wallet: str) -> List[int]:
        return self.graph.get_cma_tokens_for_wallet(wallet.lower())

    def _get_wallets(self, handle: str) -> str:
        return self.mongo.get_wallets(handle)

    def _is_eligible_for_train(self, metadata: Metadata) -> bool:

        for session in metadata.training_sessions:
            if session.command == "detection" or session.command == "mirror":
                return False

        return True

    def _spawn_new_shell(self, shell_id: int) -> Metadata:
        return Metadata(
            id=shell_id,
            image="ipfs://QmTiqSJa39nWLVXT6BJZq7QTk4TjwaWcWHjTTi8NfkunFp/2.png",
            description="cryptomanga wave #2",
            attributes=[
                Attribute(trait_type="Body", value="unknown"),
                Attribute(trait_type="Tattoo", value="unknown"),
                Attribute(trait_type="Expression", value="unknown"),
                Attribute(trait_type="Wear", value="unknown"),
                Attribute(trait_type="Head", value="unknown"),
                Attribute(trait_type="Integration", value="0", display_type="number"),
                Attribute(trait_type="Skill", value="0", display_type="number"),
                Attribute(trait_type="Combat", value="0", display_type="number"),
            ],
            training_sessions=list(),
        )

    def handle(self, data: Dict):

        status_id = data["tweet_create_events"][0]["id"]

        try:
            handle = self._extract_handle(data)
            text = self._extract_text(data)
            text = self._sanitize_text(text)
            command = self._extract_command(text)
            wallets = self._get_wallets(handle)
            cmd = Command[command]
            now = datetime.datetime.now()

            for wallet in wallets:

                if cmd == Command.train:
                    _, choice, _ = text.split()  # !train <choice> @CryptoMangaBot
                    if not (choice == "detection" or choice == "mirror"):
                        return

                    shell_ids = self._shells_for_wallet(wallet)

                    if shell_ids is None or len(shell_ids) == 0:
                        continue

                    chosen_shell = random.choice(shell_ids)
                    chosen_shell_outcome = None
                    chosen_shell_skill = None
                    chosen_shell_combat = None
                    chosen_shell_mentor = None

                    for idx, shell_id in enumerate(shell_ids):

                        metadata = Metadata.query.filter_by(id=shell_id).first()

                        if metadata is None:
                            metadata = self._spawn_new_shell(shell_id)
                            db.session.add(metadata)

                        if not self._is_eligible_for_train(metadata):
                            return

                        skill_change = None
                        combat_change = None

                        if choice == "detection":
                            coin_flip = bernoulli(0.85)

                            if coin_flip == 1:
                                skill_change = max(5, int(normal(25, 2)))
                                combat_change = max(5, int(normal(25, 3)))

                                if shell_id == chosen_shell:
                                    chosen_shell_outcome = (
                                        GameOutcome.DETECTION_INCREASE
                                    )
                                    chosen_shell_skill = skill_change
                                    chosen_shell_combat = combat_change
                                metadata.update("Skill", skill_change)
                                metadata.update("Combat", combat_change)
                            else:
                                skill_change = -2
                                combat_change = -3

                                if shell_id == chosen_shell:
                                    chosen_shell_outcome = (
                                        GameOutcome.DETECTION_DECREASE
                                    )
                                    chosen_shell_skill = skill_change
                                    chosen_shell_combat = combat_change
                                metadata.update("Skill", skill_change)
                                metadata.update("Combat", combat_change)

                        elif choice == "mirror":

                            lvl = metadata.add_mentor()
                            skill_change = 0
                            combat_change = 0

                            if shell_id == chosen_shell:
                                chosen_shell_outcome = GameOutcome.MIRROR
                                chosen_shell_skill = skill_change
                                chosen_shell_combat = combat_change
                                chosen_shell_mentor = lvl

                        metadata.training_sessions.append(
                            Training(
                                training_date=now,
                                command=choice,
                                skill_change=skill_change,
                                combat_change=combat_change,
                                handle=handle,
                                force=0,
                            )
                        )

                    dispatch = ResponseDispatch()

                    response_text = dispatch.execute(
                        chosen_shell,
                        chosen_shell_outcome,
                        chosen_shell_skill,
                        chosen_shell_combat,
                        chosen_shell_mentor,
                    )

                    self.twitter.execute(
                        handle,
                        response_text,
                        in_reply_to_status_id=status_id,
                    )
                    db.session.commit()

            else:
                return

        except:
            return
