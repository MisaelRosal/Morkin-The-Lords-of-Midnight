import random
import os
from entities.player import Player
from entities.enemy import Enemy
from world.map import GameMap
from systems.combat import CombatSystem
from core.commands import move, show_help, DIRECTIONS
from core.character_creation import create_character, print_stats
from systems.exploration import explore

ENEMIES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "enemies.json")

class Game:
    def __init__(self):
        self.player = None
        self.game_map = GameMap()
        self.current_enemy = None
        self.in_combat = False

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

    def run(self):
        print("=" * 45)
        print("   MORKIN: THE LORDS OF MIDNIGHT")
        print("=" * 45)
        print()
        print("Escribe 'ayuda' para ver los comandos.\n")

        self.player = create_character()

        location = self.game_map.get_location(self.player.position)
        print(f"\nComienzas en {location.name}.")
        print(f"{location.description}")

        while True:
            command = input("\n> ").strip().lower()

            if command == "salir":
                print("Gracias por jugar!")
                break

            if command == "ayuda":
                print(show_help())
                continue

            if command == "estado":
                print_stats(self.player)
                continue

            if command in DIRECTIONS:
                success, message = move(self.player, self.game_map, command)
                print(message)
                if success:
                    location = self.game_map.get_location(self.player.position)
                    print(location.description)
                    self.random_encounter()
                    if self.in_combat:
                        if not self.run_combat():
                            break
                continue

            if command == "explorar":
                print(explore(self.player))
                self.random_encounter()
                if self.in_combat:
                    if not self.run_combat():
                        break
                continue

            print("Comando no reconocido. Escribe 'ayuda' para ver los comandos.")
