from abc import ABC, abstractmethod
from typing import Optional, Set, Tuple

from cryptomanga import db
from cryptomanga.battle.state import BattleState
from cryptomanga.battle.workshop import WorkshopApi
from cryptomanga.handler.mongo_api import MongoApi
from cryptomanga.handler.sampling import normal
from cryptomanga.handler.the_graph_api import TheGraphApi
from cryptomanga.handler.twitter_api import TwitterApi
from cryptomanga.persistence.cache.heroku_redis import HerokuRedis
from cryptomanga.persistence.model import DarkBattle, Metadata


class BaseCommand:
    def __init__(
        self,
        redis: HerokuRedis,
        mongo: MongoApi,
        graph: TheGraphApi,
        twitter: TwitterApi,
        workshop: WorkshopApi,
    ) -> None:
        self.redis = redis
        self.mongo = mongo
        self.graph = graph
        self.twitter = twitter
        self.workshop = workshop

    def _construct_redis_key(self, p1: str, p2: str) -> str:
        return f"{p1}:{p2}"

    def _load_or_create(self, shell_id: int) -> DarkBattle:
        shell = DarkBattle.query.filter_by(id=shell_id).first()
        if not shell:
            shell = DarkBattle(shell_id=shell_id, won=0, lost=0, skill=0, combat=0)
        return shell

    def _process_end_of_battle(self, battle: BattleState):
        winner: DarkBattle = self._load_or_create(battle.get_winner_shell())
        loser: DarkBattle = self._load_or_create(battle.get_loser_shell())

        p1, p2 = (
            Metadata.query.filter_by(id=int(battle.p1_shell)).first(),
            Metadata.query.filter_by(id=int(battle.p2_shell)).first(),
        )
        winning_shell: Metadata = (
            p1 if battle.get_winner_shell() == battle.p1_shell else p2
        )

        losing_shell: Metadata = (
            p1 if battle.get_loser_shell() == battle.p1_shell else p2
        )

        winning_shell_value = winning_shell.shell_value()
        losing_shell_value = losing_shell.shell_value()

        skill_increase = 0
        combat_increase = 0

        if winning_shell_value < losing_shell_value:
            # upset, higher point increase
            delta = losing_shell_value - winning_shell_value
            if 0 < delta < 25:
                skill_increase += int(max(0, normal(5, 2)))
                combat_increase += int(max(0, normal(5, 2)))
            elif 25 < delta < 50:
                skill_increase += int(max(0, normal(10, 2)))
                combat_increase += int(max(0, normal(10, 2)))
            elif 50 < delta < 100:
                skill_increase += int(max(0, normal(15, 2)))
                combat_increase += int(max(0, normal(15, 2)))
            else:
                skill_increase += int(max(0, normal(20, 2)))
                combat_increase += int(max(0, normal(20, 2)))

        else:
            delta = winning_shell_value - losing_shell_value
            if 0 < delta < 25:
                skill_increase += int(max(0, normal(5, 2)))
                combat_increase += int(max(0, normal(5, 2)))
            elif 25 < delta < 50:
                skill_increase += int(max(0, normal(10, 2)))
                combat_increase += int(max(0, normal(10, 2)))
            elif 50 < delta < 100:
                skill_increase += int(max(0, normal(15, 2)))
                combat_increase += int(max(0, normal(15, 2)))
            else:
                skill_increase += int(max(0, normal(20, 2)))
                combat_increase += int(max(0, normal(20, 2)))

        print("increase", skill_increase, combat_increase)

        winner.process_win(skill=skill_increase, combat=combat_increase)
        loser.process_loss(skill=2, combat=4)

        winning_shell.add_battle_victory()

        db.session.add(winner)
        db.session.add(loser)
        db.session.add(winning_shell)
        db.session.commit()

        self.redis.delete(battle.p1)
        self.redis.delete(battle.p2)
        self.redis.delete(self._construct_redis_key(battle.p1, battle.p2))

        return winner, loser

    def _get_shells(self, handle: str) -> Set[int]:
        # all_shells = list()
        # wallets = self.mongo.get_wallets(handle)

        # for wallet in wallets:
        #     all_shells.extend(self.graph.get_cma_tokens_for_wallet(wallet.lower()))
        if handle == "amplituhedron":
            return [979]
        elif handle == "eluminol":
            return [993]
        else:
            return []

    def _is_valid_workshop_item_holder(self, handle: str, item: str) -> bool:
        wallets = self.mongo.get_wallets(handle)

        for wallet in wallets:
            if self.workshop.does_wallet_own_asset(wallet.lower(), item):
                return True

        return False

    def _load_battle_state(self, handle: str) -> Optional[BattleState]:
        key = self.redis.get(handle)

        if key is None:
            return None

        return BattleState.deserialize(self.redis.get(key))

    def _get_current_player_metadata(self, battle: BattleState) -> Metadata:

        player_map = {
            BattleState.P1: Metadata.query.filter_by(id=int(battle.p1_shell)).first(),
            BattleState.P2: Metadata.query.filter_by(id=int(battle.p2_shell)).first(),
        }

        return player_map.get(battle.get_current_player_idx())

    def _get_metadata(self, battle: BattleState) -> Tuple[Metadata, Metadata]:
        return (
            Metadata.query.filter_by(id=int(battle.p1_shell)).first(),
            Metadata.query.filter_by(id=int(battle.p2_shell)).first(),
        )

    @abstractmethod
    def execute(self, text: str, handle: str, status_id: int) -> BattleState:
        pass
