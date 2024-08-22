from datetime import datetime

from cryptomanga.persistence.model import Metadata


class SessionsHandler:

    COMMAND_MULTIPLIERS = {
        "spawn": 21,
        "gym": 20,
        "study": 20,
        "blaster": 19,
        "herb": 19,
        "rest": 16,
        "stealth": 16,
        "aqua": 16,
        "shroom": 14,
        "chill": 14,
        "item": 13,
        "research": 13,
        "scale": 12,
        "stay": 12,
        "hall": 1,
        "vault": 9,
        "proto": 8,
        "neo": 8,
        "helix": 7,
        "shell": 7,
        "rat": 5,
        "tiko": 5,
        "ceremony": 4,
        "celebration": 1,
        "glove": 2,
        "neo_2": 2,
        "token": 1,
        "lore": 1,
        "combat": 1,
        "run": 8,
        "ritual": 1,
        "wet": 1,
        "battleplan": 1,
        "strategy": 1,
        "walking": 1,
        "desert": 1,
        "detection": 1,
        "mirror": 1,
    }

    def handle(self, id: int):
        result = Metadata.query.filter_by(id=int(id)).first()
        sessions = result.training_sessions
        sessions.sort(key=lambda x: x.training_date)
        ret_val = list()

        for session in sessions:
            serialized = session.serialize()
            multiplier = None
            if (
                session.command == "neo"
            ):  # special case because command is not unique :(
                multiplier = 2 if session.training_date > datetime(2021, 12, 19) else 8

            elif session.command == "vault":
                multiplier = 1 if session.training_date > datetime(2021, 12, 30) else 9
            elif session.command == "blaster":
                multiplier = 1 if session.training_date > datetime(2021, 12, 30) else 19
            elif session.command == "shroom":
                multiplier = 1 if session.training_date > datetime(2021, 12, 30) else 14
            elif session.command == "aqua":
                multiplier = 1 if session.training_date > datetime(2021, 12, 30) else 16
            else:
                multiplier = SessionsHandler.COMMAND_MULTIPLIERS[session.command]
            serialized["force"] = session.force * multiplier
            ret_val.append(serialized)

        return ret_val
