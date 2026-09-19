import random
from systems.combat import check_skill, roll_d6

class ActionSystem:
    def __init__(self, player, game_map, time_system, conditions, fatigue, exploration):
        self.player = player
        self.game_map = game_map
        self.time_system = time_system
        self.conditions = conditions
        self.fatigue = fatigue
        self.exploration = exploration

    def travel(self, direction):
        if self.conditions.exhausted:
            return False, "Estas agotado. No puedes viajar. Usa 'descansar' o 'acampar'."

        weather_penalty = self.time_system.get_weather_penalty()
        orientation_skill = self.player.skills.get("orientation", 0) + weather_penalty

        roll, success = check_skill(orientation_skill)

        if success:
            from core.commands import DIRECTIONS
            if direction not in DIRECTIONS:
                return False, "Direccion no valida."

            if not self.game_map.is_valid_move(self.player.position, direction):
                return False, "No hay caminos en esa direccion."

            new_position = self.game_map.get_connection(self.player.position, direction)
            self.player.position = new_position
            location = self.game_map.get_location(new_position)

            self.fatigue.add_fatigue(self.player, 2)

            return True, f"Viajas hacia el {direction}. Llegas a {location.name}.\n{location.description}"
        else:
            deviation = roll_d6()
            if deviation <= 3:
                return True, f"Te pierdes en el camino. (Tirada: {roll})\nPermaneces en tu ubicacion actual."
            else:
                from core.commands import DIRECTIONS
                directions = list(DIRECTIONS)
                random.shuffle(directions)
                for d in directions:
                    if self.game_map.is_valid_move(self.player.position, d):
                        new_position = self.game_map.get_connection(self.player.position, d)
                        self.player.position = new_position
                        location = self.game_map.get_location(new_position)
                        self.fatigue.add_fatigue(self.player, 2)
                        return True, f"Te desvias hacia el {d}. Llegas a {location.name}.\n{location.description}"
                return True, "Te pierdes pero no encuentras salida. Te quedas donde estas."

    def camp(self):
        weather_bonus = self.time_system.get_weather_bonus()
        camp_skill = self.player.skills.get("camp", 0) + weather_bonus

        roll, success = check_skill(camp_skill)

        fatigue_reduced = 0
        hp_recovered = 0

        if success:
            fatigue_reduced = random.randint(3, 6)
            hp_recovered = random.randint(1, 4)
        else:
            fatigue_reduced = random.randint(1, 3)
            hp_recovered = random.randint(1, 2)

        self.fatigue.reduce_fatigue(self.player, fatigue_reduced)
        self.player.heal(hp_recovered)

        msg = f"Acampas exitosamente.\nFatigue -{fatigue_reduced} | HP +{hp_recovered}"

        if self.conditions.hungry:
            self.conditions.eat()
            msg += "\nComes tu ultima racion."

        return True, msg

    def forage(self):
        weather_penalty = self.time_system.get_weather_penalty()
        foraging_skill = self.player.skills.get("foraging", 0) + weather_penalty

        roll, success = check_skill(foraging_skill)

        if success:
            items = [
                ("Racion", 70),
                ("Hierbas curativas", 15),
                ("Bayas venenosas", 10),
                ("Flor rara", 5),
            ]
            total = sum(p for _, p in items)
            r = random.randint(1, total)
            cumulative = 0
            for item, prob in items:
                cumulative += prob
                if r <= cumulative:
                    if item == "Racion":
                        self.player.add_item("Racion x1")
                        return True, f"Forrajeas con exito. Encuentras: {item}"
                    elif item == "Hierbas curativas":
                        self.player.add_item("Vendajes x1")
                        return True, f"Forrajeas con exito. Encuentras: {item}"
                    else:
                        return True, f"Forrajeas con exito. Encuentras: {item}"
        return False, "No encuentras nada interesante."

    def hunt(self):
        weather_penalty = self.time_system.get_weather_penalty()
        hunting_skill = self.player.skills.get("hunting", 0) + weather_penalty

        roll, success = check_skill(hunting_skill)

        if success:
            rations = random.randint(1, 3)
            self.player.add_item(f"Racion x{rations}")
            return True, f"Cazas con exito. Obtienes {rations} raciones."
        return False, "No encuentras presas."

    def rest(self):
        fatigue_reduced = random.randint(1, 3)
        hp_recovered = random.randint(1, 2)

        self.fatigue.reduce_fatigue(self.player, fatigue_reduced)
        self.player.heal(hp_recovered)

        return True, f"Descansas.\nFatigue -{fatigue_reduced} | HP +{hp_recovered}"

    def seek(self):
        location = self.game_map.get_location(self.player.position)

        if location.name in ("Ruinas", "Fortaleza"):
            roll = random.randint(1, 66)
            if roll >= 61:
                return True, f"Encuentras una sala especial en {location.name}! (Tirada: {roll})"
            elif roll >= 31:
                enemy_roll = roll_d6()
                if enemy_roll <= 2:
                    return True, f"Encuentras un enemigo en {location.name}!"
                else:
                    return True, f"Exploras {location.name} pero no encuentras nada especial. (Tirada: {roll})"
            else:
                return True, f"Exploras {location.name} pero no encuentras nada. (Tirada: {roll})"
        else:
            return True, f"No hay nada especial que buscar en {location.name}."

    def get_available_actions(self):
        actions = []
        actions.append(("viajar [direccion]", "Moverte a otra ubicacion"))
        actions.append(("forage", "Buscar recursos"))
        actions.append(("hunt", "Cazar animales"))
        actions.append(("descansar", "Tomar un descanso"))
        actions.append(("acampar", "Establecer campamento"))

        if self.player.position in (2, 4):
            actions.append(("buscar", "Explorar ruinas/fortaleza"))

        return actions
