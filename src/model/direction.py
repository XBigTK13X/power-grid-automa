import random

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