import random

compass_lookup = {
    1: [0,'N'],
    2: [45,'NE'],
    3: [90,'E'],
    4: [135,'SE'],
    5: [180,'S'],
    6: [225,'SW'],
    7: [270,'W'],
    8: [315,'NW']
}

class Direction:
    def __init__(self,name,opposite,next,prev):
        self.name = name
        self.opposite = opposite
        self.next = next
        self.prev = prev

direction_lookup = {
    'n': Direction('n','s','ne','nw'),
    'ne': Direction('ne','sw','e','n'),
    'e': Direction('e','w','se','ne'),
    'se': Direction('se','nw','s','e'),
    's': Direction('s','n','sw','se'),
    'sw': Direction('sw','ne','w','s'),
    'w': Direction('w','e','nw','sw'),
    'nw': Direction('nw','se','n','w')
}

def get_direction(direction_key:str):
    return direction_lookup[direction_key]


def random_direction():
    return random.choice(list(direction_lookup.keys()))

def get_compass(compass_index):
    return compass_lookup[compass_index]