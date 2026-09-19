from entities.player import Player
from world.map import GameMap
from core.commands import move, show_status, show_help, DIRECTIONS

class Game:
    def __init__(self):
        self.player = None
        self.game_map = GameMap()

    def create_player(self, name):
        self.player = Player(name, health=100, gold=0)
        location = self.game_map.get_location(self.player.position)
        print(f"\nBienvenido, {name}!")
        print(f"Comienzas en {location.name}.")
        print(f"{location.description}")

    def run(self):
        print("=== Morkin: The Lords of Midnight ===")
        print("Escribe 'ayuda' para ver los comandos.\n")

        name = input("Como se llama tu personaje? ").strip()
        if not name:
            name = "Heroe"
        self.create_player(name)

        while True:
            command = input("\n> ").strip().lower()

            if command == "salir":
                print("Gracias por jugar!")
                break

            if command == "ayuda":
                print(show_help())
                continue

            if command == "estado":
                print(show_status(self.player, self.game_map))
                continue

            if command in DIRECTIONS:
                success, message = move(self.player, self.game_map, command)
                print(message)
                if success:
                    location = self.game_map.get_location(self.player.position)
                    print(location.description)
                continue

            print("Comando no reconocido. Escribe 'ayuda' para ver los comandos.")
