class Player:
    def __init__(self, name, health, gold=0):
        self.name = name
        self.health = health
        self.max_health = health
        self.valor = 0
        self.gold = gold
        self.inventory = []
        self.position = 0  # Node_id del grafo, inicia en Pradera (0)