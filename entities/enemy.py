import json
import random

class Enemy:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.type = data["type"]
        self.health = data["hp"]
        self.max_health = data["hp"]
        self.melee = data["melee"]
        self.defense = data["defense"]
        self.defense_value = data.get("defense_value", data["defense"] // 2)
        self.absorption = data.get("absorption", 0)
        self.perception = data["perception"]
        self.xp = data["xp"]
        self.damage = data.get("damage", "1d6")
        self.critical_damage = data.get("critical_damage", 5)
        self.loot_table = data.get("loot_table", "default_loot")
        self.abilities = data.get("abilities", [])
        self.attack_table = data.get("attack_table", None)
        self.critical_effect = data.get("critical_effect", None)
        self.fumble_effect = data.get("fumble_effect", None)
        self.is_unique = data.get("is_unique", False)
        self.is_boss = data.get("is_boss", False)
        self.status_effects = []

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        final_damage = max(0, damage - self.absorption)
        self.health = max(0, self.health - final_damage)
        return final_damage

    def has_status(self, status):
        return status in self.status_effects

    def add_status(self, status):
        if status not in self.status_effects:
            self.status_effects.append(status)

    def remove_status(self, status):
        if status in self.status_effects:
            self.status_effects.remove(status)

    def get_attack(self):
        if not self.attack_table:
            return {"name": "Golpe", "damage": self.damage, "effect": None}
        roll = random.randint(1, 6)
        for attack in self.attack_table:
            if attack["roll_min"] <= roll <= attack["roll_max"]:
                return attack
        return self.attack_table[0]

    def roll_loot(self, filepath=None):
        if not filepath:
            filepath = "data/loot_tables.json"
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                loot_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        table = loot_data.get(self.loot_table, [])
        if not table:
            return None

        roll = random.randint(1, 6)
        for entry in table:
            if entry["roll_min"] <= roll <= entry["roll_max"]:
                if random.randint(1, 100) <= entry.get("chance", 50):
                    return entry["item"]
        return None

    @staticmethod
    def load_from_json(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @staticmethod
    def create_random(filepath, unique_only=False, boss_only=False):
        data = Enemy.load_from_json(filepath)
        if boss_only:
            filtered = [e for e in data if e.get("is_boss")]
        elif unique_only:
            filtered = [e for e in data if e.get("is_unique")]
        else:
            filtered = [e for e in data if not e.get("is_unique")]
        if not filtered:
            filtered = data
        chosen = random.choice(filtered)
        return Enemy(chosen)

    @staticmethod
    def create_by_id(filepath, enemy_id):
        data = Enemy.load_from_json(filepath)
        for entry in data:
            if entry["id"] == enemy_id:
                return Enemy(entry)
        return None
