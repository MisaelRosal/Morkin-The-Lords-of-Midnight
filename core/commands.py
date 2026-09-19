from systems.exploration import explore

DIRECTIONS = {"norte", "sur", "este", "oeste"}

def move(player, game_map, direction):
    if direction not in DIRECTIONS:
        return False, "Direccion no valida. Usa: norte, sur, este, oeste"

    if not game_map.is_valid_move(player.position, direction):
        return False, "No hay caminos en esa direccion."

    new_position = game_map.get_connection(player.position, direction)
    player.position = new_position
    location = game_map.get_location(new_position)
    return True, f"Avanzas hacia el {direction}. Llegas a {location.name}."

def show_help():
    return (
        "Comandos disponibles:\n"
        "  norte    - Moverte al norte\n"
        "  sur      - Moverte al sur\n"
        "  este     - Moverte al este\n"
        "  oeste    - Moverte al oeste\n"
        "  explorar - Explorar tu entorno\n"
        "  estado   - Ver tu estado\n"
        "  mapa     - Ver el mapa\n"
        "  ayuda    - Ver esta ayuda\n"
        "  salir    - Salir del juego"
    )
