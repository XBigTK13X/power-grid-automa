import random

original_plants = [
    [3,2,'oil',1],
    [4,2,'coal',1],
    [5,2,'oil/coal',1],
    [6,1,'trash',1],
    [7,3,'oil',2],
    [8,3,'coal',2],
    [9,1,'oil',1],
    [10,2,'coal',2],
    [11,1,'nuke',2],
    [12,2,'oil/coal',2],
    [13,0,'wind',1],
    [14,2,'trash',2],
    [15,2,'coal',3],
    [16,2,'oil',3],
    [17,1,'nuke',2],
    [18,0,'wind',2],
    [19,2,'trash',3],
    [20,3,'coal',5],
    [21,2,'oil/coal',4],
    [22,0,'wind',4],
    [23,1,'nuke',3],
    [24,2,'trash',4],
    [25,2,'coal',5],
    [26,2,'oil',5],
    [27,0,'wind',3],
    [28,1,'nuke',4],
    [29,1,'oil/coal',3],
    [30,3,'trash',6],
    [31,3,'coal',6],
    [32,3,'oil',6],
    [33,0,'wind',4],
    [34,1,'nuke',5],
    [35,1,'oil',5],
    [36,3,'coal',7],
    [37,0,'wind',4],
    [38,3,'trash',7],
    [39,1,'nuke',6],
    [40,2,'oil',6],
    [42,2,'coal',6],
    [44,0,'wind',5],
    [46,3,'oil/coal',7],
    [50,0,'wind',6],
    [0,0,'step3',0]
]

class PlantCard:
    def __init__(self,definition:dict):
        self.cost = definition[0]
        self.resource_amount = definition[1]
        self.resource_kind = definition[2]
        self.power_output = definition[3]
        self.is_step_3 = definition[2] == 'step3'

class PlantMarket:
    def __init__(self,card_infos):
        self.cards = [PlantCard(xx) for xx in card_infos]
        self.market = []
        for ii in range(0,8):
            self.market.append(self.cards.pop(0))
        self.step_3 = self.cards.pop()
        random.shuffle(self.cards)
        self.cards.append(self.step_3)

    def is_empty(self):
        return len(self.market) <= 0

    def take_plant(self,plant_index):
        plant = self.market[plant_index]
        del self.market[plant_index]
        return plant

    def refill(self):
        if len(self.market) < 8 and len(self.cards) > 0:
            next_card = self.cards.pop(0)
            if not next_card.is_step_3:
                self.market.append(next_card)
                self.market = sorted(self.market,key=lambda xx: xx.cost)
            return next_card.is_step_3
        False

    def random(self):
        ii = random.randint(0,len(self.market)-1)
        plant = self.market[ii]
        del self.market[ii]
        return plant

    def replace(self,plant):
        self.market.append(plant)
        self.market = sorted(self.market,key=lambda xx: xx.cost)

    def cycle_highest(self):
        if len(self.market) <= 0:
            return False
        highest = self.market.pop()
        self.cards.append(highest)
        return self.refill()

    def remove_lowest(self):
        if len(self.market) > 0:
            self.market.pop(0)

    def has_plant(self,index):
        return len(self.market) > index