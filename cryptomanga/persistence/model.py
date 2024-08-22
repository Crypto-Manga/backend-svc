import time

from cryptomanga import db


class Attribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trait_type = db.Column(db.Text, nullable=False)
    value = db.Column(
        db.String, nullable=False
    )  # This could be a string or a number (float, integer)
    display_type = db.Column(db.String, nullable=True)
    metadata_id = db.Column(
        db.Integer, db.ForeignKey("metadata.id", ondelete="CASCADE"), nullable=False
    )


class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metadata_id = db.Column(db.Integer, db.ForeignKey("metadata.id"))

    training_date = db.Column(db.DateTime, nullable=False)
    command = db.Column(db.Text, nullable=False)
    skill_change = db.Column(db.Integer, nullable=False)
    combat_change = db.Column(db.Integer, nullable=False)
    handle = db.Column(db.Text, nullable=False)
    force = db.Column(db.Float, nullable=False)

    def serialize(self):
        return {
            "command": self.command,
            "skill_change": self.skill_change,
            "combat_change": self.combat_change,
            # "force": self.force, this is calculated separately as it is cumulative
            "training_date": time.mktime(self.training_date.timetuple()),
        }


class DarkBattle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shell_id = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Integer, nullable=False)
    lost = db.Column(db.Integer, nullable=False)
    skill = db.Column(db.Integer, nullable=False)
    combat = db.Column(db.Integer, nullable=False)

    def process_win(self, skill=0, combat=0):
        self.won += 1
        self.skill += skill
        self.combat += combat

    def process_loss(self, skill=0, combat=0):
        self.lost += 1
        self.skill += skill
        self.combat += combat

    def serialize(self):
        return {
            "shell_id": self.shell_id,
            "won": self.won,
            "lost": self.lost,
            "skill": self.skill,
            "combat": self.combat,
        }


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)

    training_sessions = db.relationship("Training", backref="training", lazy=True)

    attributes = db.relationship("Attribute", backref="attribute", lazy="dynamic")

    def update(self, attr_name: str, value: int) -> None:
        for attribute in self.attributes:
            if attribute.trait_type == attr_name:
                attribute.value = str(int(attribute.value) + value)

    def add_collectible(self, trait_type: str, value: str) -> None:
        self.attributes.append(Attribute(trait_type=trait_type, value=value))

    def add_mentor(self) -> int:
        for attribute in self.attributes:
            if attribute.trait_type == "Mentor":
                current_level = int(attribute.value.replace("Level", "").strip())
                attribute.value = f"Level {current_level + 1}"
                return current_level + 1

        self.attributes.append(Attribute(trait_type="Mentor", value="Level 1"))
        return 1

    def add_battle_victory(self):
        for attribute in self.attributes:
            if attribute.trait_type == "Battles Won":
                attribute.value = f"{int(attribute.value) + 1}"
                return

        self.attributes.append(
            Attribute(trait_type="Battles Won", value="1", display_type="number")
        )

    def get_attribute(self, attr_name: str):
        for attribute in self.attributes:
            if attribute.trait_type == attr_name:
                return attribute.value

    def shell_value(self) -> int:
        return int(self.get_attribute("Skill")) + int(self.get_attribute("Combat"))

    @classmethod
    def create(cls, id) -> "Metadata":
        return Metadata(
            id=id,
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

    def serialize(self) -> str:

        attributes = [
            {
                k: v
                for k, v in {
                    "trait_type": attr.trait_type,
                    "value": attr.value,
                    "display_type": attr.display_type if attr.display_type else None,
                }.items()
                if v is not None
            }
            for attr in self.attributes
        ]

        return {
            "name": f"CryptoManga #{self.id}",
            "description": self.description,
            "image": self.image,
            "attributes": attributes,
        }
