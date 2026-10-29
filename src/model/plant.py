import random


class PlantCard:
    def __init__(self, definition: dict):
        self.cost = definition[0]
        self.resource_amount = definition[1]
        self.resource_kind = definition[2]
        self.power_output = definition[3]
        self.is_step_3 = definition[2] == "step3"

    def __repr__(self):
        return f"{self.cost} - {self.is_step_3}"

    def __str__(self):
        return self.__repr__()


class PlantMarket:
    def __init__(self, card_infos, plants_to_remove=8):
        all_cards = [PlantCard(xx) for xx in card_infos]
        self.market = []
        for _ in range(8):
            self.market.append(all_cards.pop(0))

        step_3_card = all_cards.pop()
        plant_thirteen = None
        remaining_pool = []
        for card in all_cards:
            if card.cost == 13 and plant_thirteen is None:
                plant_thirteen = card
            else:
                remaining_pool.append(card)

        random.shuffle(remaining_pool)
        for _ in range(plants_to_remove):
            if remaining_pool:
                remaining_pool.pop()

        self.cards = [plant_thirteen] if plant_thirteen else []
        self.cards.extend(remaining_pool)
        self.cards.append(step_3_card)

    def is_empty(self):
        return len(self.market) <= 0

    def take_plant(self, plant_index):
        plant = self.market[plant_index]
        del self.market[plant_index]
        return plant

    def refill(self):
        if len(self.cards) > 0:
            next_card = self.cards.pop(0)
            if not next_card.is_step_3:
                self.market.append(next_card)
                self.market = sorted(self.market, key=lambda xx: xx.cost)
                return False
            return True
        return False

    def random(self):
        valid_range = min(len(self.market), 4)
        if valid_range == 0:
            return None
        choice_idx = random.randint(0, valid_range - 1)
        plant = self.market[choice_idx]
        del self.market[choice_idx]
        return plant

    def replace(self, plant):
        self.market.append(plant)
        self.market = sorted(self.market, key=lambda xx: xx.cost)

    def cycle_highest(self):
        if len(self.market) <= 0:
            return False
        highest = self.market.pop()
        self.cards.append(highest)
        return self.refill()

    def remove_lowest(self):
        if len(self.market) > 0:
            return self.market.pop(0)
        return None

    def has_plant(self, index):
        return len(self.market) > index

    def get_actual_market(self):
        limit = min(len(self.market), 4)
        return list(self.market[:limit])
