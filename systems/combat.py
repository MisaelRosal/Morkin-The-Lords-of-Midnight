import random
import re

def roll_dice(notation):
    notation = notation.lower().strip()
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", notation)
    if not match:
        return 0
    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    total = sum(random.randint(1, die_size) for _ in range(num_dice))
    return max(0, total + modifier)

def roll_d100():
    return random.randint(1, 100)

def roll_d6():
    return random.randint(1, 6)

def roll_d10():
    return random.randint(1, 10)

def check_skill(skill_value):
    roll = roll_d100()
    success = roll <= skill_value
    return roll, success

def is_critical(roll):
    return roll < 5

def is_fumble(roll):
    return roll == 100

def calculate_damage(damage_notation):
    return roll_dice(damage_notation)

def apply_armor(damage, defense_value):
    return max(0, damage - defense_value)

def initiative_check():
    return roll_d10()

def critical_table():
    result = roll_d6()
    effects = {
        1: ("Golpe preciso", "Danio maximo"),
        2: ("Golpe brutal", "Danio maximo +1"),
        3: ("Aturdimiento", "Danio maximo + Stunned"),
        4: ("Golpe devastador", "Danio maximo +2"),
        5: ("Frenesi", "Ataque adicional"),
        6: ("Muerte instantanea", "Solo si no es inmune"),
    }
    return result, effects[result]

def fumble_table():
    result = roll_d6()
    effects = {
        1: ("Fallo", "El ataque falla"),
        2: ("Torpeza", "-20 Melee hasta siguiente turno"),
        3: ("Paralisis", "Pierde proximo turno"),
        4: ("Golpe aliado", "Golpea aliado cercano"),
        5: ("Herida leve", "Recibe 1d6-2 de danio"),
        6: ("Herida grave", "Recibe 1d6 de danio"),
    }
    return result, effects[result]

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.round_num = 0
        self.combat_log = []
        self.player_initiative = 0
        self.enemy_initiative = 0
        self.player_turn = True
        self.combat_active = True

    def log(self, message):
        self.combat_log.append(message)

    def start(self):
        self.player_initiative = initiative_check()
        self.enemy_initiative = initiative_check()
        self.log(f"--- INICIO DEL COMBATE ---")
        self.log(f"Enemigo: {self.enemy.name} ({self.enemy.health} HP)")
        self.log(f"Tu iniciativa: {self.player_initiative} | Enemigo: {self.enemy_initiative}")
        if self.player_initiative >= self.enemy_initiative:
            self.player_turn = True
            self.log("Actuas primero.")
        else:
            self.player_turn = False
            self.log("El enemigo actua primero.")
        self.log("")

    def player_attack(self):
        melee = self.player.skills.get("melee", 0)
        roll, success = check_skill(melee)
        self.log(f"--- Tu turno ---")
        self.log(f"Atacas con Melee ({melee}). Tirada: {roll}")

        if is_critical(roll):
            crit_id, crit_desc = critical_table()
            self.log(f"CRITICO! (tirada < 5)")
            self.log(f"Efecto: {crit_desc[0]} - {crit_desc[1]}")
            weapon = self.player.equipment.get("weapon")
            damage_str = weapon.get("damage", "1d6") if weapon else "1d6"
            max_damage = roll_dice(damage_str)
            actual = self.enemy.take_damage(max_damage)
            self.log(f"Danio critico a {self.enemy.name}: {actual} HP")
            if not self.enemy.is_alive():
                return self.victory()
            return True

        if is_fumble(roll):
            fumble_id, fumble_desc = fumble_table()
            self.log(f"PIFIA! (tirada = 100)")
            self.log(f"Efecto: {fumble_desc[0]} - {fumble_desc[1]}")
            return True

        if not success:
            self.log("El ataque falla.")
            return True

        weapon = self.player.equipment.get("weapon")
        damage_str = weapon.get("damage", "1d6") if weapon else "1d6"
        damage = calculate_damage(damage_str)
        final_damage = apply_armor(damage, self.enemy.defense_value)
        self.log(f"Danio base: {damage} | Armadura: {self.enemy.defense_value} | Final: {final_damage}")
        actual = self.enemy.take_damage(final_damage)
        self.log(f"{self.enemy.name} recibe {actual} HP de danio. (HP: {self.enemy.health}/{self.enemy.max_health})")

        if not self.enemy.is_alive():
            return self.victory()
        return True

    def enemy_attack(self):
        roll, success = check_skill(self.enemy.melee)
        self.log(f"--- Turno de {self.enemy.name} ---")
        self.log(f"{self.enemy.name} ataca. Tirada: {roll}")

        if is_critical(roll):
            crit_id, crit_desc = critical_table()
            self.log(f"CRITICO enemigo! (tirada < 5)")
            self.log(f"Efecto: {crit_desc[0]} - {crit_desc[1]}")
            actual = self.player.take_damage(self.enemy.critical_damage)
            self.log(f"Danio critico a ti: {actual} HP")
            if not self.player.is_alive():
                return self.defeat()
            return True

        if is_fumble(roll):
            fumble_id, fumble_desc = fumble_table()
            self.log(f"PIFIA enemiga! (tirada = 100)")
            self.log(f"Efecto: {fumble_desc[0]} - {fumble_desc[1]}")
            return True

        if not success:
            self.log(f"{self.enemy.name} falla el ataque.")
            return True

        damage = calculate_damage(self.enemy.damage)
        defence_value = self.player.get_defence_value()
        final_damage = apply_armor(damage, defence_value)
        self.log(f"Danio base: {damage} | Tu armadura: {defence_value} | Final: {final_damage}")
        actual = self.player.take_damage(final_damage)
        self.log(f"Recibes {actual} HP de danio. (HP: {self.player.hp['current']}/{self.player.hp['max']})")

        if not self.player.is_alive():
            return self.defeat()
        return True

    def player_flee(self):
        self.log(f"--- Tu turno ---")
        self.log("Intentas huir...")
        defence = self.player.skills.get("defence", 0)
        roll, success = check_skill(defence)
        if success:
            self.log(f"Escapas del combate! (tirada: {roll})")
            self.combat_active = False
            return True
        else:
            self.log(f"Fallaste al huir. (tirada: {roll})")
            self.log("El enemigo te ataca mientras intentas escapar.")
            return self.enemy_attack()

    def victory(self):
        self.combat_active = False
        self.log("")
        self.log(f"=== VICTORIA ===")
        self.log(f"Has derrotado a {self.enemy.name}!")
        self.log(f"Recompensa: {self.enemy.xp} XP")
        return True

    def defeat(self):
        self.combat_active = False
        self.log("")
        self.log(f"=== DERROTA ===")
        self.log(f"Has sido derrotado por {self.enemy.name}.")
        return True

    def get_combat_log(self):
        return "\n".join(self.combat_log)
