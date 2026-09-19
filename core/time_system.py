import random

QUARTERS = ["Morning", "Afternoon", "Evening", "Night"]
QUARTER_NAMES = {"Morning": "Manana", "Afternoon": "Tarde", "Evening": "Atardecer", "Night": "Noche"}

WEATHER_CLEAR = "Clear"
WEATHER_NORMAL = "Normal"
WEATHER_HEAVY = "Heavy"

class TimeSystem:
    def __init__(self):
        self.day = 1
        self.quarter_index = 0
        self.weather = WEATHER_NORMAL
        self.previous_weather = WEATHER_NORMAL

    def current_quarter(self):
        return QUARTERS[self.quarter_index]

    def current_quarter_name(self):
        return QUARTER_NAMES[self.current_quarter()]

    def advance_quarter(self):
        self.quarter_index += 1
        if self.quarter_index >= 4:
            self.quarter_index = 0
            self.day += 1
            return True
        return False

    def is_night(self):
        return self.current_quarter() == "Night"

    def roll_weather(self):
        roll = random.randint(1, 10)
        if roll == 1:
            self.weather = WEATHER_HEAVY
        elif roll in (2, 3):
            self.weather = WEATHER_CLEAR
        elif roll in (4, 5, 6, 7, 8):
            self.weather = WEATHER_NORMAL
        else:
            self.weather = self.previous_weather
        self.previous_weather = self.weather
        return self.weather

    def get_weather_penalty(self):
        if self.weather == WEATHER_HEAVY:
            return -20
        return 0

    def get_weather_bonus(self):
        if self.weather == WEATHER_CLEAR:
            return 10
        return 0

    def get_weather_description(self):
        if self.weather == WEATHER_CLEAR:
            return "El cielo esta despejado."
        elif self.weather == WEATHER_HEAVY:
            return "El viento sopla con fuerza."
        return "Clima normal."

    def __str__(self):
        return f"Dia {self.day} - {self.current_quarter_name()} [{self.weather}]"


class ConditionsSystem:
    def __init__(self):
        self.hungry = False
        self.exhausted = False
        self.poisoned = False
        self.bleeding = False
        self.days_without_food = 0

    def check_hunger(self, player):
        if self.hungry:
            self.days_without_food += 1
            player.fatigue["current"] += 4
            if self.days_without_food >= 6:
                return "GAME_OVER_HUNGER"
        return None

    def eat(self):
        self.hungry = False
        self.days_without_food = 0

    def apply_starvation(self, player):
        if self.hungry:
            self.days_without_food += 1
            player.fatigue["current"] += 4
            if self.days_without_food >= 6:
                return True
        return False

    def check_exhaustion(self, player):
        self.exhausted = player.fatigue["current"] > player.fatigue["max"]
        return self.exhausted

    def apply_poison(self):
        self.poisoned = True

    def cure_poison(self):
        self.poisoned = False

    def apply_bleeding(self):
        self.bleeding = True

    def cure_bleeding(self):
        self.bleeding = False

    def apply_daily_effects(self, player):
        messages = []
        if self.poisoned:
            player.hp["current"] = max(0, player.hp["current"] - 2)
            messages.append("Pierdes 2 HP por veneno.")
        if self.bleeding:
            player.hp["current"] = max(0, player.hp["current"] - 4)
            messages.append("Pierdes 4 HP por sangrado.")
        if self.hungry:
            player.fatigue["current"] += 4
            messages.append("Pierdes 4 Fatigue por hambre.")
        return messages

    def get_status_messages(self):
        messages = []
        if self.hungry:
            messages.append(f"HAMBRIENTO ({self.days_without_food} dias sin comer)")
        if self.exhausted:
            messages.append("AGOTADO (no puede viajar)")
        if self.poisoned:
            messages.append("ENVENENADO (-2 HP/dia)")
        if self.bleeding:
            messages.append("SANGRANDO (-4 HP/dia)")
        return messages


class FatigueSystem:
    def __init__(self):
        pass

    def get_max_fatigue(self, player):
        return player.attributes["str"] // 5

    def add_fatigue(self, player, amount):
        player.fatigue["current"] += amount
        return player.fatigue["current"] > player.fatigue["max"]

    def reduce_fatigue(self, player, amount):
        player.fatigue["current"] = max(0, player.fatigue["current"] - amount)

    def is_exhausted(self, player):
        return player.fatigue["current"] > player.fatigue["max"]


class IceFearSystem:
    def __init__(self):
        self.level = 1

    def check_recruitment(self):
        roll = random.randint(1, 6)
        fail_threshold = self.level
        if roll <= fail_threshold:
            return False, roll
        return True, roll

    def increase_level(self):
        if self.level < 3:
            self.level += 1

    def decrease_level(self):
        if self.level > 1:
            self.level -= 1
