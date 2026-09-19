class Player:
    def __init__(self, name, health, gold=0):
        self.name = name
        self.health = health
        self.max_health = health
        self.valor = 0
        self.gold = gold
        self.inventory = []
        self.position = 0

        self.melee = 50
        self.defense = 50
        self.defense_value = 25
        self.endurance = 50
        self.mental_toughness = 50
        self.absorption = 0
        self.status_effects = []

    def is_alive(self):
        return self.health > 0

    def is_wounded(self):
        return self.health < 10

    def take_damage(self, damage):
        final_damage = max(0, damage - self.absorption)
        self.health = max(0, self.health - final_damage)
        return final_damage

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def has_status(self, status):
        return status in self.status_effects

    def add_status(self, status):
        if status not in self.status_effects:
            self.status_effects.append(status)

    def remove_status(self, status):
        if status in self.status_effects:
            self.status_effects.remove(status)
