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
    20: 150
}

class Human:
    def __init__(self):
        self.money = 50
        self.plants = []
        self.resources = {
            'coal': 0,
            'oil': 0,
            'trash': 0,
            'nuke': 0
        }
        self.houses = 0
        self.cities = []
        self.city_names = []

    def debug(self):
        debug.game('=-Human-=')
        debug.game(f'  resources -> {self.resources}')
        debug.game(f'  money {self.money}')
        debug.game("  plants")
        debug.game([f'  #{x.cost} - {x.resource_kind} x {x.resource_amount} => {x.power_output}' for x in self.plants])
        debug.game(f'  points {self.houses}')
        debug.game(f'  cities')
        debug.game(f'  {self.city_names}')

    def purchase_plant(self,plant_market,new_plant,ante,can_ignore=True):
        if not can_ignore:
            self.money -= new_plant.cost + ante
            self.plants.append(new_plant)
            return True
        if self.money < new_plant.cost + ante:
            return False
        if self.power_capacity() > self.houses:
            return False
        if self.power_capacity() >= 15:
            return False
        for plant in self.plants:
            if plant.power_output < new_plant.power_output or len(self.plants) < 3:
                self.money -= new_plant.cost + ante
                self.plants.append(new_plant)
                self.plants = sorted(self.plants,key=lambda xx:xx.cost)
                if len(self.plants) > 3:
                    self.plants.pop(0)
                return True
        return False

    def get_highest_plant(self):
        return self.plants[-1]

    def purchase_resources(self,resource_market):
        balance = deepcopy(self.resources)
        houses_served = 0
        orders = []
        self.plants.reverse()
        resource_order = []
        for plant in self.plants:
            if plant.resource_kind == 'wind':
                houses_served += plant.power_output
                continue
            if houses_served >= self.houses and self.houses > 0:
                break
            # TODO Handle oil/coal properly
            resource_to_claim = plant.resource_kind
            if plant.resource_kind == 'oil/coal':
                resource_to_claim = random.choice(['oil','coal'])
            balance[resource_to_claim] -= plant.resource_amount
            houses_served += plant.power_output
            if not resource_to_claim in resource_order and balance[resource_to_claim] < 0:
                resource_order.append(resource_to_claim)
        self.plants.reverse()
        filled_orders = []
        for order in resource_order:
            if balance[order] < 0:
                debug.game(f"Wallet has ${self.money}. Requesting {-balance[order]} {order}")
                cost,amount = resource_market.cost_to_buy(order,-balance[order])
                if cost <= self.money:
                    purchased,post_money,taken = resource_market.purchase(order,-balance[order],self.money)
                    self.money = post_money
                    debug.game(f"Human bought {taken} {order}")
                    self.resources[order] += taken
                    filled_orders.append([order,taken,f'${cost}'])
                else:
                    debug.game(f"Human didn't have enough money for {-balance[order]} {order}")
        return filled_orders

    def build_houses(self,game_map,step):
        if self.houses == 0:
            destination,money = game_map.first_human_city()
            debug.sim(f"Human built first house in {destination.name}")
            destination.build_house(1,'Human')
            self.cities.append(destination)
            self.city_names.append(destination.name)
            self.houses += 1
            return 1,10
        else:
            can_afford = True
            built = 0
            total_cost = 0
            while can_afford and self.houses < CITY_WIN_COUNT:
                destination = random.choice(self.cities)
                direction = model.random_direction()
                target,city_with_connection_cost = game_map.next_human_city(self.money,direction,destination,step,self.city_names)
                if target == None:
                    debug.game("Human could not find an open city")
                    break
                if city_with_connection_cost < self.money:
                    debug.game(f'Human building in {target.name} for ${city_with_connection_cost}')
                    target.build_house(step,'Human')
                    self.cities.append(target)
                    self.city_names.append(target.name)
                    self.houses += 1
                    self.money -= city_with_connection_cost
                    total_cost += city_with_connection_cost
                    built += 1
                else:
                    can_afford = False
            if built == 0:
                if self.houses >= CITY_WIN_COUNT:
                    debug.game(f'Human does not need to build any more houses')
                else:
                    debug.game(f'Human cannot afford to build this turn')
            return built,total_cost

    def power_cities(self):
        max_powered = self.houses
        powered = 0
        power_plants = sorted(self.plants,key=lambda xx: xx.power_output)
        power_plants.reverse()
        for plant in power_plants:
            if plant.resource_kind == 'wind':
                powered += plant.power_output
                continue
            if powered < max_powered:
                # TODO properly handle oil/coal
                resource_kind = plant.resource_kind
                if plant.resource_kind == 'oil/coal':
                    resource_kind = 'oil' if self.resources['oil'] > self.resources['coal'] else 'coal'
                if self.resources[resource_kind] >= plant.resource_amount:
                    self.resources[resource_kind] -= plant.resource_amount
                    powered += plant.power_output
        if powered > max_powered:
            powered = max_powered
        debug.game(f'Human powered {powered} cities and made {power_payouts[powered]} money')
        self.money += power_payouts[powered]

    def power_capacity(self):
        return sum(x.power_output for x in self.plants)