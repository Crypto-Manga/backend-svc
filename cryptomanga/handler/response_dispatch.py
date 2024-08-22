import random

from cryptomanga.handler.enums import GameOutcome

detection_increase = [
    """Result for #{shell_id}

🟢💎 Shells that evade the blast triggers left by the patrols of both friends (+ foes) will be key to victory when the DB comes.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 🌱⚡️""",
    """Result for #{shell_id}

🟢💿 You weaved right through the detection beams in the Mirror Chamber! Take your success today as a sign of great promise.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🟢⛓ eNyra throws great praise onto your shell's stealth. You entered the Mirror Chamber – and this training – a rookie, yet left a legend.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🟢🔎 eNyra is one of the more ~elusive~ of the Masters here – yet she will be watching your every move when the the time of DB comes.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🟢🔎 eNyra is one of the more ~elusive~ of the Masters here – yet she will be watching your every move when the the time of DB comes.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🟢💎 The Mirror Chamber is an all-seeing zone — + you proved your stealth under great pressure today.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
]


detection_decrease = [
    """Result for #{shell_id}

🔻⚡️ Your shell got caught out by the zone's detection beams — eNyra won't be here to get you out of trouble when the DB comes!

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🔻💥 The Mirror Chamber contains a series of hidden blast triggers – your shell took the brunt of them today.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🔻⛓  The Mirror Chamber is all-seeing, and you were unlucky to feel the wrath of its gaze (and those detection beams) in today's session.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🔻🚨 The Mirror Chamber refused to let you pass — trip up like that (literally) in the DB and you'll suffer more than just a bruised ego...

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
    """Result for #{shell_id}

🔻⚡️ It's better to make these mistakes now than in the heat of the DarkBattle, when one wrong move could signal the end for your shell.

Skill EXP {skill}
Combat EXP {combat}

The training sprint is complete — view your EXP growth in the Cabinet. 💥""",
]


mirror = [
    """Result for #{shell_id}

🟢👁 Looks like someone's been running drills back in the Academy... eNyra may have a future rival on her hands! 

MENTOR #{mentor} attained.

Mentoring phase complete. Check your Cabinet to view final results. 🌱""",
    """Result for #{shell_id}

🟢🐍 You've developed into one nimble shell since your first training... looks like someone was out to impress eNyra today.

MENTOR #{mentor} attained.

Mentoring phase complete. Check your Cabinet to view final results. 🌱""",
    """Result for #{shell_id}

🟢⚔️ Returning to the fabled Mirror Chamber as a mentor is always risky – yet you made it outta there unscathed!

MENTOR #{mentor} attained.

Mentoring phase complete. Check your Cabinet to view final results. 🌱""",
    """Result for #{shell_id}                     

🟢👘 Final shot at a Yukata — did you make it count?

MENTOR #{mentor} attained.

Mentoring phase complete. Check your Cabinet to view final results. 🌱""",
]


class ResponseDispatch:
    def execute(
        self, shell_id: int, outcome: GameOutcome, skill: int, combat: int, mentor: int
    ):
        if outcome == GameOutcome.DETECTION_INCREASE:
            return random.choice(detection_increase).format(
                shell_id=shell_id, skill=skill, combat=combat, mentor=mentor
            )
        elif outcome == GameOutcome.DETECTION_DECREASE:
            return random.choice(detection_decrease).format(
                shell_id=shell_id, skill=skill, combat=combat, mentor=mentor
            )

        elif outcome == GameOutcome.MIRROR:
            return random.choice(mirror).format(
                shell_id=shell_id, skill=skill, combat=combat, mentor=mentor
            )
