import math

class Player:
    def __init__(self):
        self.name = "Morkin"
        self.attributes = {"str": 0, "dex": 0, "int": 0, "cha": 0}
        self.skills = {}
        self.specialization = None
        self.hp = {"current": 0, "max": 0}
        self.fatigue = {"current": 0, "max": 0}
        self.silver = 0
        self.horse = False
        self.position = 0
        self.inventory = []
        self.equipment = {
            "armor": None,
            "helmet": None,
            "cape": None,
            "amulet": None,
            "weapon": None,
        }
        self.weapons_carried = []
        self.max_weapons = 3
        self.backpack_size = 6
        self.status_effects = []
        self.xp = 0

    def calculate_skills(self):
        s = self.attributes
        self.skills = {
            "animal_handling": s["cha"],
            "athletics": s["dex"],
            "camp": (s["dex"] // 2) + (s["int"] // 2),
            "defence": (s["str"] // 2) + (s["dex"] // 2),
            "disarm_traps": (s["dex"] // 2) + (s["int"] // 2),
            "endurance": s["str"],
            "first_aid": s["int"],
            "fishing": s["dex"],
            "foraging": (s["dex"] // 2) + (s["int"] // 2),
            "hunting": (s["str"] // 2) + (s["dex"] // 2),
            "lock_picking": (s["dex"] // 2) + (s["int"] // 2),
            "might": s["str"],
            "mental_toughness": (s["int"] // 2) + (s["cha"] // 2),
            "melee": s["str"],
            "orientation": s["int"],
            "perception": s["int"],
            "persuasion": s["cha"],
            "stealth": s["dex"],
        }

    def apply_specialization(self):
        if not self.specialization:
            return
        specs = {
            "Weapon Master": {"melee": 10},
            "Shield Master": {"defence": 10},
            "Scout": {"perception": 10},
            "Ranger": {"camp": 10},
            "Locksmith": {"lock_picking": 10},
            "Animal Trainer": {"animal_handling": 10},
            "Medic": {"first_aid": 10},
            "Harvester": {"foraging": 10},
            "Hunter": {"hunting": 10},
            "Pathfinder": {"orientation": 10},
            "Shadowstalker": {"stealth": 10},
        }
        bonuses = specs.get(self.specialization, {})
        for skill, bonus in bonuses.items():
            if skill in self.skills:
                self.skills[skill] = min(60, self.skills[skill] + bonus)

    def apply_spec_items(self):
        if self.specialization == "Locksmith":
            self.add_item("Lockpicks x5")
        elif self.specialization == "Animal Trainer":
            self.add_item("Rations x5")
        elif self.specialization == "Medic":
            self.add_item("Bandages x5")
        elif self.specialization == "Harvester":
            self.add_item("Simple Foraging Knife")
            self.skills["foraging"] = min(60, self.skills["foraging"] + 5)
        elif self.specialization == "Hunter":
            self.add_item("Hunter's Sling")
            self.skills["hunting"] = min(60, self.skills["hunting"] + 5)
        elif self.specialization == "Shadowstalker":
            self.add_item("Fogstone x1")

    def calculate_derived(self):
        self.hp["max"] = 50
        self.hp["current"] = 50
        self.fatigue["max"] = self.attributes["str"] // 5
        self.fatigue["current"] = 0
        self.silver = self.attributes["cha"] // 2
        self.horse = True

    def get_defence_value(self):
        return self.skills.get("defence", 0) // 2

    def get_absorption(self):
        if self.equipment["armor"]:
            return self.equipment["armor"].get("absorption", 0)
        return 0

    def is_alive(self):
        return self.hp["current"] > 0

    def is_wounded(self):
        return self.hp["current"] < 10

    def take_damage(self, damage):
        absorption = self.get_absorption()
        final_damage = max(0, damage - absorption)
        self.hp["current"] = max(0, self.hp["current"] - final_damage)
        return final_damage

    def heal(self, amount):
        self.hp["current"] = min(self.hp["max"], self.hp["current"] + amount)

    def add_item(self, item):
        if len(self.inventory) < self.backpack_size:
            self.inventory.append(item)
            return True
        return False

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def has_status(self, status):
        return status in self.status_effects

    def add_status(self, status):
        if status not in self.status_effects:
            self.status_effects.append(status)

    def remove_status(self, status):
        if status in self.status_effects:
            self.status_effects.remove(status)

    def to_dict(self):
        return {
            "name": self.name,
            "attributes": self.attributes,
            "skills": self.skills,
            "specialization": self.specialization,
            "hp": self.hp,
            "fatigue": self.fatigue,
            "silver": self.silver,
            "horse": self.horse,
            "position": self.position,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "xp": self.xp,
        }
