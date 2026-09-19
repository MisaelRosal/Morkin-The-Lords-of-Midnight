import random
import os
from entities.player import Player
from entities.enemy import Enemy
from world.map import GameMap
from systems.combat import CombatSystem
from core.commands import move, show_help, DIRECTIONS
from core.character_creation import create_character, print_stats
from systems.exploration import explore
from core.time_system import TimeSystem, ConditionsSystem, FatigueSystem, IceFearSystem
from core.actions import ActionSystem

ENEMIES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "enemies.json")

class Game:
    def __init__(self):
        self.player = None
        self.game_map = GameMap()
        self.current_enemy = None
        self.in_combat = False
        self.time_system = TimeSystem()
        self.conditions = ConditionsSystem()
        self.fatigue_system = FatigueSystem()
        self.ice_fear = IceFearSystem()
        self.action_system = None
        self.running = True

    def random_encounter(self):
        if random.randint(1, 100) <= 30:
            self.current_enemy = Enemy.create_random(ENEMIES_FILE)
            self.in_combat = True
            print(f"\nUn {self.current_enemy.name} aparece!")
            print(f"HP: {self.current_enemy.health} | Melee: {self.current_enemy.melee}")

    def run_combat(self):
        combat = CombatSystem(self.player, self.current_enemy)
        combat.start()
        print(combat.get_combat_log())
        combat.combat_log.clear()

        if not combat.player_turn:
            print(f"\n{self.current_enemy.name} ataca primero!")
            combat.enemy_attack()
            print(combat.get_combat_log())
            combat.combat_log.clear()
            combat.player_turn = True

        while combat.combat_active:
            command = input("\n> [combate] ").strip().lower()

            if command == "atacar":
                combat.player_attack()
                print(combat.get_combat_log())
                combat.combat_log.clear()

                if combat.combat_active:
                    if self.conditions.poisoned:
                        self.current_enemy.take_damage(1)
                        print(f"El veneno afecta al enemigo. -1 HP")
                    combat.enemy_attack()
                    print(combat.get_combat_log())
                    combat.combat_log.clear()

            elif command == "huir":
                combat.player_flee()
                print(combat.get_combat_log())
                combat.combat_log.clear()

                if combat.combat_active:
                    combat.enemy_attack()
                    print(combat.get_combat_log())
                    combat.combat_log.clear()

            elif command == "estado":
                print_stats(self.player)

            elif command == "ayuda":
                print("Combate: 'atacar' para atacar, 'huir' para escapar")

            else:
                print("Comando de combate: 'atacar', 'huir', 'estado'")

        if not self.player.is_alive():
            print("\nHas muerto. Fin del juego.")
            return False

        if self.current_enemy and not self.current_enemy.is_alive():
            self.player.silver += random.randint(1, 5)
            self.player.xp += self.current_enemy.xp

        self.current_enemy = None
        self.in_combat = False
        return True

    def advance_quarter(self):
        new_day = self.time_system.advance_quarter()

        if new_day:
            print(f"\n=== NUEVO DIA {self.time_system.day} ===")
            self.time_system.roll_weather()
            print(self.time_system.get_weather_description())

            daily_messages = self.conditions.apply_daily_effects(self.player)
            for msg in daily_messages:
                print(msg)

            game_over = self.conditions.apply_starvation(self.player)
            if game_over:
                print("\nHas muerto de hambre. Fin del juego.")
                self.running = False
                return

            self.conditions.check_exhaustion(self.player)

        print(f"\n{self.time_system}")

    def show_time_status(self):
        print(f"\n{self.time_system}")
        print(f"Dia: {self.time_system.day} | Cuarto: {self.time_system.current_quarter_name()}")
        print(f"Clima: {self.time_system.weather}")

        status_msgs = self.conditions.get_status_messages()
        if status_msgs:
            for msg in status_msgs:
                print(f"  * {msg}")

        print(f"Fatigue: {self.player.fatigue['current']}/{self.player.fatigue['max']}")

    def show_actions(self):
        actions = self.action_system.get_available_actions()
        print("\nAcciones disponibles:")
        for cmd, desc in actions:
            print(f"  {cmd} - {desc}")

    def run(self):
        print("=" * 45)
        print("   MORKIN: THE LORDS OF MIDNIGHT")
        print("   Flow of Play")
        print("=" * 45)
        print()

        self.player = create_character()
        self.player.fatigue["max"] = self.player.attributes["str"] // 5

        self.action_system = ActionSystem(
            self.player, self.game_map, self.time_system,
            self.conditions, self.fatigue_system, None
        )

        self.time_system.roll_weather()
        print(f"\nDia {self.time_system.day} - {self.time_system.current_quarter_name()}")
        print(self.time_system.get_weather_description())

        location = self.game_map.get_location(self.player.position)
        print(f"\nComienzas en {location.name}.")
        print(f"{location.description}")

        while self.running:
            self.show_time_status()

            command = input("\n> ").strip().lower()

            if command == "salir":
                print("Gracias por jugar!")
                break

            if command == "ayuda":
                print(show_help())
                print("  viajar [direccion] - Moverte a otra ubicacion")
                print("  forage - Buscar recursos")
                print("  hunt - Cazar animales")
                print("  descansar - Tomar un descanso")
                print("  acampar - Establecer campamento")
                print("  buscar - Explorar ruinas/fortaleza")
                print("  hora - Ver hora y clima")
                print("  acciones - Ver acciones disponibles")
                continue

            if command == "hora":
                self.show_time_status()
                continue

            if command == "acciones":
                self.show_actions()
                continue

            if command == "estado":
                print_stats(self.player)
                continue

            if command.startswith("viajar"):
                parts = command.split()
                if len(parts) < 2:
                    print("Uso: viajar [norte/sur/este/oeste]")
                    continue
                direction = parts[1]
                success, message = self.action_system.travel(direction)
                print(message)
                if success:
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                self.advance_quarter()
                continue

            if command == "forage":
                success, message = self.action_system.forage()
                print(message)
                if success and random.randint(1, 100) <= 20:
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                self.advance_quarter()
                continue

            if command == "hunt":
                success, message = self.action_system.hunt()
                print(message)
                if success and random.randint(1, 100) <= 25:
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                self.advance_quarter()
                continue

            if command == "descansar":
                success, message = self.action_system.rest()
                print(message)
                self.advance_quarter()
                continue

            if command == "acampar":
                if self.time_system.current_quarter() != "Night":
                    print("Solo puedes acampar de noche.")
                    continue
                success, message = self.action_system.camp()
                print(message)
                self.advance_quarter()
                continue

            if command == "buscar":
                success, message = self.action_system.seek()
                print(message)
                if "enemigo" in message.lower():
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                self.advance_quarter()
                continue

            if command == "explorar":
                print(explore(self.player))
                self.random_encounter()
                if self.in_combat:
                    if not self.run_combat():
                        break
                self.advance_quarter()
                continue

            if command in DIRECTIONS:
                success, message = self.action_system.travel(command)
                print(message)
                if success:
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                self.advance_quarter()
                continue

            print("Comando no reconocido. Escribe 'ayuda' para ver los comandos.")

        print("\n=== JUEGO TERMINADO ===")
        print(f"Sobreviviste {self.time_system.day} dias.")
