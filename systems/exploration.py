import random
from world.events import LOCATION_EVENTS

def explore(player):
    events = LOCATION_EVENTS.get(player.position, [])
    if not events:
        return "No hay nada interesante aqui."
    return random.choice(events)
