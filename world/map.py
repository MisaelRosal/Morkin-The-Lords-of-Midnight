class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class GameMap:
    def __init__(self):
        self.locations = {
            0: Location("Pradera", "Un campo abierto de hierba verde."),
            1: Location("Bosque", "Arboles altos bloquean la luz del sol."),
            2: Location("Ruinas", "Antiguas estructuras cubiertas de musgo."),
            3: Location("Montaña", "Picos rocosos se alzan ante ti."),
            4: Location("Fortaleza", "Una fortaleza imponente domina el horizonte."),
        }

        self.connections = {
            0: {"norte": 1, "este": 2, "sur": 3},
            1: {"sur": 0, "este": 2},
            2: {"oeste": 0, "sur": 3},
            3: {"norte": 0, "este": 2, "sur": 4},
            4: {"norte": 3},
        }

    def get_location(self, node_id):
        return self.locations.get(node_id)

    def get_connection(self, node_id, direction):
        return self.connections.get(node_id, {}).get(direction)

    def is_valid_move(self, node_id, direction):
        return direction in self.connections.get(node_id, {})
