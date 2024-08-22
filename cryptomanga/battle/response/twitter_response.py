from cryptomanga.battle.response.bone_zombie import BONE_ZOMBIE
from cryptomanga.battle.response.helios import HELIOS
from cryptomanga.battle.response.machina_cyberdog import MACHINA_CYBERDOG
from cryptomanga.battle.response.ocean import OCEAN
from cryptomanga.battle.response.reptilian import REPTILIAN
from cryptomanga.battle.response.snow_ice import SNOW_ICE
from cryptomanga.battle.response.solar import SOLAR


def get_response(command: str, body_type: str):

    mapping = {
        "solar": SOLAR,
        "snow": SNOW_ICE,
        "ice": SNOW_ICE,
        "ocean": OCEAN,
        "reptilian": REPTILIAN,
        "helios": HELIOS,
        "bone": BONE_ZOMBIE,
        "zombie": BONE_ZOMBIE,
        "cyberdog": MACHINA_CYBERDOG,
        "machina": MACHINA_CYBERDOG,
    }

    return mapping.get(body_type).get(command)
