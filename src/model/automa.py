import random
from copy import deepcopy

import src.debug as debug

LEFT_SIDE = 0
RIGHT_SIDE = 1


class AutomaCardHalf:
    def __init__(
        self,
        plant,
        ante,
        resource_amount,
        build_direction,
        build_amount,
    ):
        self.market_choice = plant
        self.market_ante = ante
        self.resource_amount = resource_amount
        self.build_direction = build_direction
        self.build_amount = build_amount


class AutomaCard:
    def __init__(self, definition):
        self.definition = definition
        self.left_half = AutomaCardHalf(
            definition["market1"],
            definition["ante1"],
            definition["resource1"],
            definition["compass_direction_1"],
            definition["build1"],
        )
        self.right_half = AutomaCardHalf(
            definition["market2"],
            definition["ante2"],
            definition["resource2"],
            definition["compass_direction_2"],
            definition["build2"],
        )


class AutomaPlayer:
    def __init__(self, name):
        self.name = name
        self.plant_stack_max = 3
        self.money = 10000
        self.houses = 0
        self.plant_stack = []
        self.build_target = None
        self.cities = []
        self.city_names = []

    def debug(self):
        debug.game(f"=-{self.name}-=")
        debug.game("  plants")
        debug.game(
            f"  {[f'#{xx.cost} - {xx.resource_kind} x {xx.resource_amount} => {xx.power_output}' for xx in self.plant_stack]}"
        )
        debug.game(f"  cities {len(self.city_names)}")
        debug.game(f"{self.city_names}")

    def claim_plant(self, plant):
        if len(self.plant_stack) < 1:
            self.plant_stack.append(plant)
        else:
            if self.plant_stack[0].cost > plant.cost:
                self.plant_stack.insert(1, plant)
            else:
                self.plant_stack.insert(0, plant)
        if len(self.plant_stack) > self.plant_stack_max:
            self.plant_stack.pop()
        return self.plant_stack

    def build_houses(self, houses_to_build, direction, game_map, step):
        debug.game(
            f"=={self.name} building {houses_to_build} houses {direction} of {self.build_target.name if self.build_target else 'random city'} during step {step}"
        )
        built = 0
        last_city = None
        for ii in range(houses_to_build):
            debug.game(f"{self.name} placing house {ii + 1} of {houses_to_build}")
            if self.houses == 0:
                build_city, build_cost = game_map.first_automa_city(
                    direction, self.name
                )
                if build_city is not None:
                    build_city.build_house(step, self.name)
                    self.build_target = build_city
                    debug.game(f"{self.name} first city is {self.build_target.name}")
                    self.cities.append(self.build_target)
                    self.city_names.append(self.build_target.name)
                    last_city = self.build_target
                self.houses += 1
                built += 1
            else:
                build_city, build_cost = game_map.next_automa_city(
                    direction, self.build_target, step, self.name
                )
                if build_city is not None and build_cost is not None:
                    debug.game(f"{self.name} built in {build_city.name}")
                    last_city = build_city
                    build_city.build_house(step, self.name)
                    self.cities.append(build_city)
                    self.city_names.append(build_city.name)
                else:
                    debug.game(f"{self.name} unable to find a free city")
                self.houses += 1
                built += 1
        if last_city is not None:
            self.build_target = last_city
        return built


class Automa:
    def __init__(self, card_infos):
        self.money = 10000
        self.deck = [AutomaCard(xx) for xx in card_infos]
        random.shuffle(self.deck)
        self.discard = []
        if len(self.deck) > 3:
            for _ in range(3):
                self.discard.append(self.deck.pop())
        self.phase_cards = []
        self.left_player = AutomaPlayer("LeftAutoma")
        self.right_player = AutomaPlayer("RightAutoma")

    def debug(self):
        debug.game("=-= Left Automa Player =-=")
        self.left_player.debug()
        debug.game("=-= Right Automa Player =-=")
        self.right_player.debug()

    def tiebreaker(self):
        left_top = (
            self.left_player.plant_stack[0].cost if self.left_player.plant_stack else 0
        )
        right_top = (
            self.right_player.plant_stack[0].cost
            if self.right_player.plant_stack
            else 0
        )
        return max(left_top, right_top)

    def draw_card(self):
        if len(self.deck) <= 0:
            self.deck = list(self.discard)
            self.discard = []
            random.shuffle(self.deck)
            if len(self.deck) > 3:
                for _ in range(3):
                    self.discard.append(self.deck.pop())
        return self.deck.pop(0)

    def draw_cards(self):
        if len(self.phase_cards) > 0:
            self.discard.extend(self.phase_cards)
            self.phase_cards = []
        self.phase_cards = [self.draw_card(), self.draw_card(), self.draw_card()]

    def claim_plant(self, plant, side):
        player = self.left_player if side == LEFT_SIDE else self.right_player
        return player.claim_plant(plant)

    def get_plant_auction_index(self, side):
        first_card = self.phase_cards[0]
        card_half = first_card.left_half if side == LEFT_SIDE else first_card.right_half
        return card_half.market_choice

    def get_current_ante(self, sides_that_bought):
        highest_ante = 0
        first_card = self.phase_cards[0]
        for side_idx in [LEFT_SIDE, RIGHT_SIDE]:
            if side_idx not in sides_that_bought:
                card_half = (
                    first_card.left_half
                    if side_idx == LEFT_SIDE
                    else first_card.right_half
                )
                if card_half.market_ante > highest_ante:
                    highest_ante = card_half.market_ante
        return highest_ante

    def get_resource_purchase_plants(self, side):
        second_card = self.phase_cards[1]
        player = self.left_player if side == LEFT_SIDE else self.right_player
        active_half = (
            second_card.left_half if side == LEFT_SIDE else second_card.right_half
        )
        if active_half.resource_amount == 0:
            return []
        if active_half.resource_amount == 1:
            return player.plant_stack
        if active_half.resource_amount == 2:
            stack = deepcopy(player.plant_stack)
            if stack:
                stack[0].resource_amount *= 2
            return stack
        return []

    def get_build_score(self):
        return self.phase_cards[2].score

    def build_houses(self, game_map, step, side):
        player = self.left_player if side == LEFT_SIDE else self.right_player
        third_card = self.phase_cards[2]
        active_half = (
            third_card.left_half if side == LEFT_SIDE else third_card.right_half
        )
        direction = active_half.build_direction.lower()
        return player.build_houses(active_half.build_amount, direction, game_map, step)

    def has_market_skips(self):
        first_card = self.phase_cards[0]
        return (
            first_card.left_half.market_choice <= 0
            or first_card.right_half.market_choice <= 0
        )
