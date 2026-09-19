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

    @staticmethod
    def load_from_json(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @staticmethod
    def create_random(filepath):
        data = Enemy.load_from_json(filepath)
        chosen = random.choice(data)
        return Enemy(chosen)

    @staticmethod
    def create_by_id(filepath, enemy_id):
        data = Enemy.load_from_json(filepath)
        for entry in data:
            if entry["id"] == enemy_id:
                return Enemy(entry)
        return None
