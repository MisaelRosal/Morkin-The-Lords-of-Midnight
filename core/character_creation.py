from entities.player import Player

VALUES = [50, 40, 30, 20]

SPECIALIZATIONS = {
    "1": {"name": "Weapon Master", "desc": "+10 Melee", "bonus": {"melee": 10}},
    "2": {"name": "Shield Master", "desc": "+10 Defence", "bonus": {"defence": 10}},
    "3": {"name": "Scout", "desc": "+10 Perception", "bonus": {"perception": 10}},
    "4": {"name": "Ranger", "desc": "+10 Camp", "bonus": {"camp": 10}},
    "5": {"name": "Locksmith", "desc": "+10 Lock-picking, +5 Lockpicks", "bonus": {"lock_picking": 10}},
    "6": {"name": "Animal Trainer", "desc": "+10 Animal Handling, +5 Rations", "bonus": {"animal_handling": 10}},
    "7": {"name": "Medic", "desc": "+10 First Aid, +5 Bandages", "bonus": {"first_aid": 10}},
    "8": {"name": "Harvester", "desc": "+10 Foraging, Foraging Knife", "bonus": {"foraging": 10}},
    "9": {"name": "Hunter", "desc": "+10 Hunting, Hunter's Sling", "bonus": {"hunting": 10}},
    "10": {"name": "Pathfinder", "desc": "+10 Orientation", "bonus": {"orientation": 10}},
    "11": {"name": "Shadowstalker", "desc": "+10 Stealth, Fogstone", "bonus": {"stealth": 10}},
}

def get_input(prompt, valid_fn=None, error_msg="Valor no valido"):
    while True:
        value = input(prompt).strip()
        if valid_fn is None or valid_fn(value):
            return value
        print(error_msg)

def create_character():
    print("=" * 45)
    print("   MORKIN: THE LORDS OF MIDNIGHT")
    print("   Creacion de Personaje")
    print("=" * 45)
    print()
    print("Morkin es mitad Humano, mitad Fey.")
    print("No existen razas, clases ni niveles.")
    print()

    player = Player()

    print("--- PASO 1: Distribuir Atributos ---")
    print(f"Valores a asignar: {VALUES}")
    print("Los 4 valores van a STR, DEX, INT, CHA (uno cada uno).")
    print()
    print("Ejemplo: STR=50, DEX=40, INT=30, CHA=20")
    print()

    attr_names = ["STR", "DEX", "INT", "CHA"]
    attr_keys = ["str", "dex", "int", "cha"]
    available = list(VALUES)

    for i, (name, key) in enumerate(zip(attr_names, attr_keys)):
        print(f"Valores disponibles: {available}")
        while True:
            try:
                val = int(input(f"  {name} = "))
                if val in available:
                    player.attributes[key] = val
                    available.remove(val)
                    break
                else:
                    print(f"  Valor no disponible. Elige de: {available}")
            except ValueError:
                print("  Ingresa un numero.")

    print()
    print("Atributos asignados:")
    for name, key in zip(attr_names, attr_keys):
        print(f"  {name} = {player.attributes[key]}")

    player.calculate_skills()

    print()
    print("--- PASO 2: Puntos de Habilidad ---")
    print("Tienes 50 puntos para distribuir en habilidades.")
    print("Ninguna habilidad puede superar 60.")
    print("Escribe 'ver' para ver habilidades, 'fin' para terminar.")
    print()

    skill_names = {
        "animal_handling": "Animal Handling",
        "athletics": "Athletics",
        "camp": "Camp",
        "defence": "Defence",
        "disarm_traps": "Disarm Traps",
        "endurance": "Endurance",
        "first_aid": "First Aid",
        "fishing": "Fishing",
        "foraging": "Foraging",
        "hunting": "Hunting",
        "lock_picking": "Lock-picking",
        "might": "Might",
        "mental_toughness": "Mental Toughness",
        "melee": "Melee",
        "orientation": "Orientation",
        "perception": "Perception",
        "persuasion": "Persuasion",
        "stealth": "Stealth",
    }

    points = 50
    while points > 0:
        print(f"Puntos restantes: {points}")
        cmd = input("Habilidad (nombre o 'fin'): ").strip().lower()

        if cmd == "fin":
            break
        if cmd == "ver":
            print()
            for key, name in skill_names.items():
                print(f"  {name}: {player.skills[key]}")
            print()
            continue

        matched_key = None
        for key, name in skill_names.items():
            if cmd == key or cmd == name.lower():
                matched_key = key
                break

        if not matched_key:
            print("Habilidad no encontrada.")
            continue

        current = player.skills[matched_key]
        max_val = 60
        space = max_val - current
        if space <= 0:
            print(f"{skill_names[matched_key]} ya esta en {current} (max 60).")
            continue

        try:
            pts = int(input(f"  Puntos para {skill_names[matched_key]} (actual: {current}, max a agregar: {min(space, points)}): "))
            if pts < 0:
                print("  No puedes usar numeros negativos.")
                continue
            if pts > points:
                print("  No tienes suficientes puntos.")
                continue
            if pts > space:
                print(f"  Solo puedes agregar {space} puntos mas.")
                continue
            player.skills[matched_key] += pts
            points -= pts
            print(f"  {skill_names[matched_key]} ahora es {player.skills[matched_key]}")
        except ValueError:
            print("  Ingresa un numero.")

    print()
    print("--- PASO 3: Especializacion ---")
    print("Elige UNA especializacion:")
    print()
    for key, spec in SPECIALIZATIONS.items():
        print(f"  {key}. {spec['name']} - {spec['desc']}")
    print()

    while True:
        choice = get_input("Elige (1-11): ", lambda x: x in SPECIALIZATIONS, "Elige un numero del 1 al 11.")
        player.specialization = SPECIALIZATIONS[choice]["name"]
        break

    player.apply_specialization()
    player.apply_spec_items()

    print()
    print(f"Especializacion elegida: {player.specialization}")

    player.calculate_derived()

    print()
    print("--- PASO 4: Compra de Equipo ---")
    print(f"Presupuesto: {player.silver} monedas de plata")
    print("(El dinero sobrante se pierde)")
    print()

    shop = [
        ("Espada de hierro", 8, {"type": "weapon", "damage": "1d6+2", "absorption": 0}),
        ("Escudo de madera", 6, {"type": "armor", "absorption": 1}),
        ("Cota de malla", 15, {"type": "armor", "absorption": 2}),
        ("Casco de hierro", 5, {"type": "helmet", "absorption": 1}),
        ("Capa de cuero", 3, {"type": "cape", "absorption": 0}),
        ("Amuleto de la suerte", 10, {"type": "amulet", "bonus": "luck"}),
        ("Antorcha", 1, {"type": "tool"}),
        ("Cuerda (10m)", 2, {"type": "tool"}),
        ("Vendajes x3", 4, {"type": "healing"}),
        ("Raciones x5", 3, {"type": "food"}),
    ]

    print("Objetos disponibles:")
    for i, (name, price, _) in enumerate(shop, 1):
        print(f"  {i}. {name} - {price} plata")
    print()
    print("Escribe los numeros separados por coma (ej: 1,3,5) o 'fin' para continuar.")
    print()

    while True:
        cmd = input(f"Comprar (tienes {player.silver} plata): ").strip().lower()
        if cmd == "fin":
            break
        try:
            choices = [int(x.strip()) for x in cmd.split(",")]
            for c in choices:
                if 1 <= c <= len(shop):
                    name, price, data = shop[c - 1]
                    if player.silver >= price:
                        if player.add_item(name):
                            player.silver -= price
                            print(f"  Compraste: {name} (-{price} plata)")
                        else:
                            print("  Mochila llena!")
                    else:
                        print(f"  No tienes suficiente plata para {name}.")
                else:
                    print(f"  Numero invalido: {c}")
        except ValueError:
            print("  Formato invalido. Usa: 1,3,5")

    print()
    print("=" * 45)
    print("   PERSONAJE COMPLETADO")
    print("=" * 44)
    print()
    print_stats(player)
    return player

def print_stats(player):
    attr_names = {"str": "STR", "dex": "DEX", "int": "INT", "cha": "CHA"}
    print("Atributos:")
    for key, name in attr_names.items():
        print(f"  {name}: {player.attributes[key]}")
    print()
    print(f"Especializacion: {player.specialization}")
    print(f"HP: {player.hp['current']}/{player.hp['max']}")
    print(f"Fatigue: {player.fatigue['current']}/{player.fatigue['max']}")
    print(f"Silver: {player.silver}")
    print(f"Horse: {'Si' if player.horse else 'No'}")
    print(f"XP: {player.xp}")
    print()
    print("Habilidades:")
    skill_names = {
        "melee": "Melee", "defence": "Defence", "perception": "Perception",
        "stealth": "Stealth", "endurance": "Endurance", "might": "Might",
        "athletics": "Athletics", "camp": "Camp", "first_aid": "First Aid",
        "foraging": "Foraging", "hunting": "Hunting", "fishing": "Fishing",
        "lock_picking": "Lock-picking", "disarm_traps": "Disarm Traps",
        "animal_handling": "Animal Handling", "persuasion": "Persuasion",
        "orientation": "Orientation", "mental_toughness": "Mental Toughness",
    }
    for key, name in skill_names.items():
        print(f"  {name}: {player.skills[key]}")
    print()
    if player.inventory:
        print(f"Inventario ({len(player.inventory)}/{player.backpack_size}):")
        for item in player.inventory:
            print(f"  - {item}")
    else:
        print("Inventario: vacio")
