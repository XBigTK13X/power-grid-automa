DEBUG_GAME=True
DEBUG_SIM=True

def game(message):
    if DEBUG_GAME:
        print(message)

def sim(message):
    if DEBUG_SIM:
        print(message)