from copy import deepcopy
import random

import src.debug as debug
import src.model as model

CITY_WIN_COUNT = 17

power_payouts = {
    0: 10,
    1: 22,
    2: 33,
    3: 44,
    4: 54,
    5: 64,
    6: 73,
    7: 82,
    8: 90,
    9: 98,
    10: 105,
    11: 112,
    12: 118,
    13: 124,
    14: 129,
    15: 134,
    16: 138,
    17: 142,
    18: 145,
    19: 148,
    20: 150,
}


class Human:
    def __init__(self):
        self.money = 50
        self.plants = []
        self.resources = {"coal": 0, "oil": 0, "trash": 0, "nuke": 0}
        self.houses = 0
        self.cities = []
        self.city_names = []

    def debug(self):
        debug.game("=-Human-=")
        debug.game(f"  resources -> {self.resources}")
        debug.game(f"  money {self.money}")
        debug.game("  plants")
        debug.game(
            [
                f"  #{xx.cost} - {xx.resource_kind} x {xx.resource_amount} => {xx.power_output}"
                for xx in self.plants
            ]
        )
        debug.game(f"  cities {len(self.city_names)}")
        debug.game(f"  {self.city_names}")

    def wants_plant(self, new_plant, ante, can_ignore=True):
        total_cost = new_plant.cost + ante
        if self.money < total_cost:
            return False

        if not can_ignore:
            return True

        if len(self.plants) < 3:
            if self.houses == 0:
                return (self.money - total_cost) >= 20
            return (self.money - total_cost) >= 10

        worst_plant = min(
            self.plants, key=lambda xx: (xx.power_output, -xx.resource_amount)
        )
        if new_plant.power_output > worst_plant.power_output:
            if self.power_capacity() < CITY_WIN_COUNT:
                return True
            if new_plant.power_output >= 5 and worst_plant.power_output <= 3:
                return True

        return False

    def purchase_plant(self, plant_market, new_plant, ante, can_ignore=True):
        total_cost = new_plant.cost + ante
        if not can_ignore:
            self.money -= total_cost
            self.plants.append(new_plant)
            self.plants = sorted(self.plants, key=lambda xx: xx.cost)
            if len(self.plants) > 3:
                self.plants.pop(0)
            return True

        if not self.wants_plant(new_plant, ante, can_ignore):
            return False

        self.money -= total_cost
        if len(self.plants) >= 3:
            worst_plant = min(
                self.plants, key=lambda xx: (xx.power_output, -xx.resource_amount)
            )
            self.plants.remove(worst_plant)
        self.plants.append(new_plant)
        self.plants = sorted(self.plants, key=lambda xx: xx.cost)
        return True

    def choose_plant_to_auction(self, plant_market, ante):
        market_plants = plant_market.get_actual_market()
        candidates = []
        for plant in market_plants:
            if self.wants_plant(plant, ante, can_ignore=True):
                candidates.append(plant)

        if not candidates:
            return None

        candidates.sort(key=lambda xx: (xx.power_output, -xx.cost), reverse=True)
        return candidates[0]

    def get_highest_plant(self):
        return self.plants[-1] if self.plants else None

    def purchase_resources(self, resource_market):
        balance = deepcopy(self.resources)
        target_power = min(self.power_capacity(), max(self.houses + 3, 2))
        houses_served = 0
        resource_order = []

        reversed_plants = sorted(
            self.plants,
            key=lambda xx: xx.power_output / max(xx.resource_amount, 1),
            reverse=True,
        )
        for plant in reversed_plants:
            if plant.resource_kind == "wind":
                houses_served += plant.power_output
                continue
            if houses_served >= target_power:
                break
            resource_to_claim = plant.resource_kind
            if plant.resource_kind == "oil/coal":
                resource_to_claim = (
                    "coal" if balance["coal"] >= balance["oil"] else "oil"
                )
            balance[resource_to_claim] -= plant.resource_amount
            houses_served += plant.power_output
            if (
                resource_to_claim not in resource_order
                and balance[resource_to_claim] < 0
            ):
                resource_order.append(resource_to_claim)

        filled_orders = []
        for order in resource_order:
            if balance[order] < 0:
                needed = -balance[order]
                debug.game(f"Wallet has ${self.money}. Requesting {needed} {order}")
                cost, available = resource_market.cost_to_buy(order, needed)
                qty_to_buy = available
                while qty_to_buy > 0 and cost > self.money:
                    qty_to_buy -= 1
                    cost, _ = resource_market.cost_to_buy(order, qty_to_buy)

                if qty_to_buy > 0 and cost <= self.money:
                    purchased, post_money, taken = resource_market.purchase(
                        order, qty_to_buy, self.money
                    )
                    self.money = post_money
                    debug.game(f"Human bought {taken} {order}")
                    self.resources[order] += taken
                    filled_orders.append([order, taken, f"${cost}"])
                else:
                    debug.game(f"Human didn't have enough money for {needed} {order}")
        return filled_orders

    def build_houses(self, game_map, step):
        built = 0
        total_spent = 0

        if self.houses == 0:
            destination, initial_cost = game_map.first_human_city()
            if destination is None or self.money < initial_cost:
                return 0, 0
            debug.sim(f"Human built first house in {destination.name}")
            destination.build_house(1, "Human")
            self.cities.append(destination)
            self.city_names.append(destination.name)
            self.money -= initial_cost
            self.houses += 1
            built += 1
            total_spent += initial_cost

        reserve = 0 if (self.houses >= 12 or self.power_capacity() >= 14) else 10

        while self.houses < CITY_WIN_COUNT:
            if self.houses >= self.power_capacity() + 1 and self.houses < 14:
                break

            target, connection_cost = game_map.next_human_city_from_network(
                self.money, self.city_names, step
            )
            if target is None:
                debug.game(f"Human could not afford another city with ${self.money}")
                break

            if (
                connection_cost + reserve <= self.money
                or self.houses + 1 >= CITY_WIN_COUNT
            ):
                if connection_cost <= self.money:
                    debug.game(
                        f"Human building in {target.name} for ${connection_cost}"
                    )
                    target.build_house(step, "Human")
                    self.cities.append(target)
                    self.city_names.append(target.name)
                    self.houses += 1
                    self.money -= connection_cost
                    total_spent += connection_cost
                    built += 1
                else:
                    break
            else:
                break

        if built == 0:
            if self.houses >= CITY_WIN_COUNT:
                debug.game(f"Human does not need to build any more houses")
            else:
                debug.game(f"Human cannot afford to build this turn")

        return built, total_spent

    def power_cities(self):
        max_powered = self.houses
        powered = 0
        power_plants = sorted(self.plants, key=lambda xx: xx.power_output, reverse=True)
        for plant in power_plants:
            if plant.resource_kind == "wind":
                powered += plant.power_output
                continue
            if powered < max_powered:
                resource_kind = plant.resource_kind
                if plant.resource_kind == "oil/coal":
                    resource_kind = (
                        "coal"
                        if self.resources["coal"] >= self.resources["oil"]
                        else "oil"
                    )
                if self.resources[resource_kind] >= plant.resource_amount:
                    self.resources[resource_kind] -= plant.resource_amount
                    powered += plant.power_output
        powered = min(powered, max_powered)
        payout = power_payouts[powered]
        debug.game(f"Human powered {powered} cities and made {payout} money")
        self.money += payout
        return powered, payout

    def power_capacity(self):
        return sum(xx.power_output for xx in self.plants)
