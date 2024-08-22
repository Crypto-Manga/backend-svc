import datetime
import json
import random
from dataclasses import dataclass

from dateutil import parser


@dataclass
class BattleState:

    HEAL_LIMIT = 2
    MAX_HEALTH = 100
    P1 = 1
    P2 = 2

    # Twitter handles of players
    p1: str
    p2: str

    # Choice of shell
    p1_shell: int
    p2_shell: int

    # Health of players, initialize with 1000
    p1_health: float
    p2_health: float

    # Number of times heal was used
    p1_heal_limit: int
    p2_heal_limit: int

    # who gets to start the battle
    first_move: int

    # Time at which the battle was started
    start_time: datetime.datetime

    # Number of times the player has chosen a move
    turns: int

    @classmethod
    def init(cls, p1: str, p2: str, p1_shell: int) -> "BattleState":
        return cls(
            p1=p1,
            p2=p2,
            p1_shell=p1_shell,
            p2_shell=None,
            p1_health=BattleState.MAX_HEALTH,
            p2_health=BattleState.MAX_HEALTH,
            p1_heal_limit=BattleState.HEAL_LIMIT,
            p2_heal_limit=BattleState.HEAL_LIMIT,
            first_move=random.choice([BattleState.P1, BattleState.P2]),
            start_time=datetime.datetime.now(),
            turns=0,
        )

    def accept(self, p2_shell: int) -> None:
        self.p2_shell = p2_shell

    def is_over(self) -> bool:
        return self.p1_health <= 0 or self.p2_health <= 0

    def increase_health(self, value: int):

        if self.get_current_player_idx() == BattleState.P1:
            self.p1_health = min(100, self.p1_health + value)
            self.p1_heal_limit -= 1
        else:
            self.p2_health = min(100, self.p2_health + value)
            self.p2_heal_limit -= 1

    def process_knockout(self):
        if self.get_current_player_idx() == BattleState.P1:
            self.p2_health = 0
        else:
            self.p1_health = 0

    def process_strike(self, value: int):
        if self.get_current_player_idx() == BattleState.P1:
            self.p2_health -= value
        else:
            self.p1_health -= value

    def can_heal(self) -> bool:
        if self.get_current_player_idx() == BattleState.P1:
            return self.p1_heal_limit > 0
        else:
            return self.p2_heal_limit > 0

    def get_winner_shell(self) -> int:
        if self.p1_health <= 0:
            return self.p2_shell
        elif self.p2_health <= 0:
            return self.p1_shell

    def get_loser_shell(self) -> int:
        if self.p1_health <= 0:
            return self.p1_shell
        elif self.p2_health <= 0:
            return self.p2_shell

    def get_current_player(self) -> str:
        def is_even(i):
            return i % 2 == 0

        if self.first_move == BattleState.P1:
            return self.p1 if is_even(self.turns) else self.p2

        else:
            return self.p1 if not is_even(self.turns) else self.p2

    @property
    def opponent(self) -> str:
        def is_even(i):
            return i % 2 == 0

        if self.first_move == BattleState.P1:
            return self.p2 if is_even(self.turns) else self.p1

        else:
            return self.p2 if not is_even(self.turns) else self.p1

    def get_current_player_idx(self) -> int:
        def is_even(i):
            return i % 2 == 0

        if self.first_move == BattleState.P1:
            return BattleState.P1 if is_even(self.turns) else BattleState.P2

        else:
            return BattleState.P1 if not is_even(self.turns) else BattleState.P2

    def get_current_player_shell(self):
        def is_even(i):
            return i % 2 == 0

        if self.first_move == BattleState.P1:
            return self.p1_shell if is_even(self.turns) else self.p2_shell

        else:
            return self.p1_shell if not is_even(self.turns) else self.p2_shell

    def serialize(self):
        return json.dumps(
            {
                "p1": self.p1,
                "p2": self.p2,
                "p1_shell": self.p1_shell,
                "p2_shell": self.p2_shell,
                "p1_health": self.p1_health,
                "p2_health": self.p2_health,
                "p1_heal_limit": self.p1_heal_limit,
                "p2_heal_limit": self.p2_heal_limit,
                "first_move": self.first_move,
                "start_time": str(self.start_time),
                "turns": self.turns,
            }
        )

    @classmethod
    def deserialize(cls, serialized_state: str) -> "BattleState":
        state = json.loads(serialized_state)

        return cls(
            p1=state["p1"],
            p2=state["p2"],
            p1_shell=state["p1_shell"],
            p2_shell=state["p2_shell"],
            p1_health=state["p1_health"],
            p2_health=state["p2_health"],
            p1_heal_limit=state["p1_heal_limit"],
            p2_heal_limit=state["p2_heal_limit"],
            first_move=state["first_move"],
            start_time=parser.parse(state["start_time"]),
            turns=state["turns"],
        )
