import random

import src.debug as debug

class AutomaCard:
    def __init__(self,definition):
        self.definition = definition
        self.plant_auction = [definition['market1'],definition['market2']]
        self.ante = [definition['ante1'],definition['ante2']]
        self.resource_purchase = [definition['resource1'],definition['resource2']]
        self.city_build = [definition['build1'],definition['build2']]
        self.build_direction = definition['compass_direction']
        self.score = int(definition['score'])

class Automa:
    def __init__(self,player_count,card_infos):
        self.money = 10000 # Never updates, this just lets it claim plants at any cost
        self.player_count = player_count
        self.deck = [AutomaCard(xx) for xx in card_infos]
        random.shuffle(self.deck)
        self.plant_stack_max = 3
        self.discard = []
        self.phase_cards = []
        self.auction_index = 0
        self.resource_index = 0
        self.build_index = 0
        self.plant_stacks = [[],[]]
        self.resource_purchase_index = player_count - 2
        self.build_index = player_count - 2
        self.houses = 0
        self.build_target = None
        self.cities = []
        self.city_names = []

    def debug(self):
        debug.game('=-Automa Debug-=')
        debug.game("  plants")
        for stack in self.plant_stacks:
            debug.game(f"  {[f'#{x.cost} - {x.resource_kind} x {x.resource_amount} => {x.power_output}' for x in stack]}")
        debug.game(f'  points {self.houses}')
        debug.game(f'  cities {self.city_names}')

    def tiebreaker(self):
        # TODO Variant - Average of plants, not highest
        return self.plant_stacks[0][0].cost

    def draw_card(self):
        if len(self.deck) <= 0:
            self.deck = self.discard
            random.shuffle(self.deck)
            self.discard = [
                self.deck.pop(0),
                self.deck.pop(0),
                self.deck.pop(0)
            ]
        return self.deck.pop(0)

    def draw_cards(self):
        if len(self.phase_cards) > 0:
            self.discard.append(self.phase_cards.pop())
            self.discard.append(self.phase_cards.pop())
            self.discard.append(self.phase_cards.pop())
        self.phase_cards = [
            self.draw_card(),
            self.draw_card(),
            self.draw_card()
        ]

    def claim_plant(self,plant):
        stack_index = 0
        if len(self.plant_stacks[0]) > len(self.plant_stacks[1]):
            stack_index = 1
        if len(self.plant_stacks[stack_index]) < 1:
            self.plant_stacks[stack_index].append(plant)
        else:
            if self.plant_stacks[stack_index][0].cost > plant.cost:
                self.plant_stacks[stack_index].append(plant)
            else:
                self.plant_stacks[stack_index].insert(0,plant)
        if len(self.plant_stacks[stack_index]) > self.plant_stack_max:
            self.plant_stacks[stack_index] = self.plant_stacks[stack_index][0:self.plant_stack_max]

    def get_plant_auction_index(self):
        return self.phase_cards[0].plant_auction[self.auction_index]

    def get_current_ante(self):
        return self.phase_cards[0].ante[self.auction_index]

    def next_auction_index(self):
        self.auction_index += 1

    def reset_indices(self):
        self.auction_index = 0
        self.resource_purchase_index = 1
        self.build_index = 1

    def get_player_order(self,human_plant):
        human_order = 1
        for stack in self.plant_stacks:
            if stack[0].cost < human_plant.cost:
                return human_order
            human_order += 1
        return human_order

    def get_resource_purchase_mult(self):
        return 1
        mult = self.phase_cards[1].resource_purchase[self.resource_purchase_index]
        self.resource_purchase_index -= 1
        return int(mult[0])

    def get_resource_purchase_plants(self,player_index):
        if player_index > len(self.plant_stacks) - 1:
            player_index = len(self.plant_stacks) - 1
        # TODO All the plants in the stack
        return self.plant_stacks[player_index]

    def get_build_score(self):
        return self.phase_cards[2].score

    def build_houses(self,game_map,step):
        direction = self.phase_cards[2].build_direction.lower()
        debug.game(f"==Automa building {direction} of {self.build_target.name if self.build_target else 'center'} during step {step}")
        houses_to_place = self.phase_cards[2].city_build[self.build_index]
        built = 0
        true_last_city = None
        for ii in range(0,houses_to_place):
            debug.game(f'Automa placing house {ii+1} of {houses_to_place}')
            if self.houses == 0:
                self.build_target = game_map.first_automa_city(direction)
                debug.game(f'Automa first city is {self.build_target.name}')
                self.cities.append(self.build_target)
                self.city_names.append(self.build_target.name)
                self.houses += 1
                built += 1
            else:
                last_city = game_map.next_automa_city(direction,self.build_target,step,self.city_names)
                if last_city:
                    true_last_city = last_city
                    self.cities.append(last_city)
                    self.city_names.append(last_city.name)
                    debug.game(f'Automa built in {last_city.name}')
                self.houses += 1
                built += 1
        if true_last_city:
            self.build_target = true_last_city
        self.build_index -= 1
        return built

    def has_four_auction_plants(self):
        for plant in self.phase_cards[0].plant_auction:
            if plant == -1:
                return False
        return True