DEBUG_GAME=False
DEBUG_SIM=False
DEBUG_RESULT=False

def game(message):
    if DEBUG_GAME:
        print(message)

def sim(message):
    if DEBUG_SIM:
        print(message)

def result(message):
    if DEBUG_RESULT:
        print(message)