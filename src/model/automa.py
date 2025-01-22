import random

import src.debug as debug

LEFT_SIDE = 0
RIGHT_SIDE = 1

class AutomaCardHalf:
    def __init__(self,build_direction,build_amount,plant,ante):
        self.build_direction = build_direction
        self.build_amount = build_amount
        self.market_choice = plant
        self.market_ante = ante

class AutomaCard:
    def __init__(self,definition):
        self.definition = definition
        self.left_half = AutomaCardHalf(
            definition['compass_direction_1'],
            definition['build1'],
            definition['market1'],
            definition['ante1']
        )
        self.right_half = AutomaCardHalf(
            definition['compass_direction_2'],
            definition['build2'],
            definition['market2'],
            definition['ante2']
        )

        # TODO Actually use the resource skip when indicated

class AutomaPlayer:
    def __init__(self,name):
        self.name = name
        self.plant_stack_max = 3
        self.money = 10000
        self.houses = 0

        self.plant_stack = []
        self.build_target = []
        self.cities = []
        self.city_names = []

    def debug(self):
        debug.game('=-Automa Debug-=')
        debug.game("  plants")
        debug.game(f"  {[f'#{x.cost} - {x.resource_kind} x {x.resource_amount} => {x.power_output}' for x in self.plant_stack]}")
        debug.game(f'  points {self.houses}')
        debug.game(f'  cities {self.city_names}')

    def claim_plant(self,plant):
        if len(self.plant_stack) < 1:
            self.plant_stack.append(plant)
        else:
            # Tuck a new plant with lower cost immediately under the top plant
            if self.plant_stack[0].cost > plant.cost:
                self.plant_stack.insert(1,plant)
            # Otherwise set it on top of the stack
            else:
                self.plant_stack.insert(0,plant)
        if len(self.plant_stack) > self.plant_stack_max:
            self.plant_stack.pop()
        return self.plant_stack

class Automa:
    def __init__(self,card_infos):
        self.money = 10000 # Never updates, this just lets it claim plants at any cost
        self.deck = [AutomaCard(xx) for xx in card_infos]
        random.shuffle(self.deck)
        self.discard = []
        self.phase_cards = []
        self.left_player = AutomaPlayer('LeftAutoma')
        self.right_player = AutomaPlayer('RightAutoma')

    def debug(self):
        debug.game("=-= Left Automa Player =-=")
        self.left_player.debug()
        debug.game("=-= Right Automa Player =-=")
        self.right_player.debug()

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

    def claim_plant(self,plant,side):
        player = self.left_player if side == LEFT_SIDE else self.right_player
        return player.claim_plant(plant)

    def get_plant_auction_index(self,side):
        first_card = self.self.phase_cards[0]
        card_half = first_card.left_half if side == LEFT_SIDE else first_card.right_half
        return card_half.plant_auction.market_choice

    def get_current_ante(self,sides_that_bought):
        highest_ante = 0
        first_card = self.self.phase_cards[0]
        for ii in [LEFT_SIDE,RIGHT_SIDE]:
            if not ii in sides_that_bought:
                card_half = first_card.left_half if ii == LEFT_SIDE else first_card.right_half
                if card_half.ante > highest_ante:
                    highest_ante = card_half.ante
        return highest_ante

    def get_resource_purchase_plants(self,side):
        player = self.left_player if side == LEFT_SIDE else self.right_player
        return player.plant_stack

    def get_build_score(self):
        return self.phase_cards[2].score

    def build_houses(self,game_map,step):
        direction = self.phase_cards[2].build_direction.lower()
        debug.game(f"==Automa building {direction} of {self.build_target.name if self.build_target else 'center'} during step {step}")
        houses_to_place = self.phase_cards[2].city_build[self.build_index]
        built = 0
        last_city = None
        for ii in range(0,houses_to_place):
            debug.game(f'Automa placing house {ii+1} of {houses_to_place}')
            if self.houses == 0:
                build_city,build_cost = game_map.first_automa_city(direction)
                build_city.build_house(step,'automa')
                self.build_target = build_city
                debug.game(f'Automa first city is {self.build_target.name}')
                self.cities.append(self.build_target)
                self.city_names.append(self.build_target.name)
                self.houses += 1
                built += 1
            else:
                build_city,build_cost = game_map.next_automa_city(direction,self.build_target,step)
                if build_cost != None:
                    debug.game(f'Automa built in {build_city.name}')
                    last_city = build_city
                    build_city.build_house(step,'automa')
                    self.cities.append(build_city)
                    self.city_names.append(f'{build_city.name}')
                    self.houses += 1
                    built += 1
                else:
                    debug.game(f'Automa unable to find a free city')
        # Move the build target after placing all houses
        if last_city:
            self.build_target = last_city
        self.build_index -= 1
        return built

    def has_four_auction_plants(self):
        for plant in self.phase_cards[0].plant_auction:
            if plant == -1:
                return False
        return True