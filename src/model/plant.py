import random

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