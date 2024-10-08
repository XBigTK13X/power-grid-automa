from copy import deepcopy
import random

DEBUG_GAME=True

def debug_game(message):
    if DEBUG_GAME:
        print(message)

us_map = {
    'refill':[
        [5,4,3,2],
        [7,5,3,3],
        [5,6,5,2]
    ],
    'start_resources':[1,3,7,14],
    'cities': [
        [1,'seattle',3],
        [1,'portland',3],
        [1,'boise',6],
        [1,'billings',5],
        [1,'cheyenne',5],
        [1,'denver',4],
        [1,'omaha',4],
        [2,'san francisco',5],
        [2,'los angeles',3],
        [2,'san diego',3],
        [2,'phoenix',3],
        [2,'las vegas',6],
        [2,'salt lake city',5],
        [2,'santa fe',8],
        [3,'fargo',3],
        [3,'duluth',4],
        [3,'minneapolis',6],
        [3,'chicago',7],
        [3,'st. louis',5],
        [3,'knoxville',2],
        [3,'cincinnati',6],
        [4,'kansas city',7],
        [4,'oklahoma city',4],
        [4,'dallas',5],
        [4,'houston',3],
        [4,'new orleans',5],
        [4,'memphis',6],
        [4,'birmingham',4],
        [5,'miami',1],
        [5,'tampa',2],
        [5,'jacksonville',4],
        [5,'savannah',3],
        [5,'atlanta',5],
        [5,'raleigh',5],
        [5,'norfolk',2],
        [6,'detroit',5],
        [6,'pittsburgh',5],
        [6,'washington dc',3],
        [6,'philadelphia',2],
        [6,'buffalo',3],
        [6,'new york',3],
        [6,'boston',1]
    ],
    'connections': [
        ['seattle','e','billings',9],
        ['seattle','se','boise',12],
        ['seattle','sw','portland',3],
        ['portland','e','boise',13],
        ['portland','s','san francisco',24],
        ['san francisco','ne','boise',23],
        ['san francisco','e','salt lake city',27],
        ['san francisco','se','las vegas',14],
        ['san francisco','s','los angeles',9],
        ['boise','ne','billings',12],
        ['boise','e','cheyenne',24],
        ['boise','se','salt lake city',8],
        ['las vegas','ne','salt lake city',18],
        ['las vegas','sw','los angeles',9],
        ['las vegas','s','san diego',9],
        ['las vegas','se','phoenix',15],
        ['las vegas','e','santa fe',27],
        ['los angeles','se','san diego',3],
        ['san diego','e','phoenix',14],
        ['salt lake city','e','denver',21],
        ['salt lake city','se','santa fe',28],
        ['phoenix','ne','santa fe',18],
        ['billings','ne','fargo',17],
        ['billings','e','minneapolis',18],
        ['billings','se','cheyenne',9],
        ['cheyenne','ne','minneapolis',18],
        ['cheyenne','e','omaha',14],
        ['cheyenne','s','denver',0],
        ['denver','e','kansas city','16'],
        ['denver','s','santa fe',13],
        ['santa fe','ne','kansas city',16],
        ['santa fe','e','oklahoma city',15],
        ['santa fe','se','dallas',16],
        ['santa fe','s','houston',21],
        ['fargo','ne','duluth',6],
        ['fargo','se','minneapolis',6],
        ['omaha','ne','minneapolis',8],
        ['omaha','se','kansas city',5],
        ['omaha','e','chicago',13],
        ['kansas city','ne','chicago',8],
        ['kansas city','e','st. louis',6],
        ['kansas city','se','memphis',12],
        ['kansas city','sw','oklahoma city',8],
        ['oklahoma city','e','memphis',14],
        ['oklahoma city','s','dallas',3],
        ['dallas','ne','memphis',12],
        ['dallas','se','new orleans',12],
        ['dallas','s','houston',5],
        ['houston','e','new orleans',8],
        ['duluth','se','detroit',15],
        ['duluth','s','chicago',12],
        ['duluth','sw','minneapolis',5],
        ['minneapolis','se','chicago',8],
        ['chicago','ne','detroit',7],
        ['chicago','se','cincinnati',7],
        ['chicago','s','st. louis',10],
        ['st. louis','e','cincinnati',12],
        ['st. louis','se','atlanta',12],
        ['st. louis','s','memphis',7],
        ['memphis','se','birmingham',6],
        ['memphis','s','new orleans',7],
        ['new orleans','ne','birmingham',11],
        ['new orleans','e','jacksonville',16],
        ['birmingham','ne','atlanta',3],
        ['birmingham','se','jacksonville',9],
        ['detroit','e','buffalo',7],
        ['detroit','se','pittsburgh',6],
        ['detroit','s','cincinnati',4],
        ['cincinnati','ne','pittsburgh',7],
        ['cincinnati','se','raleigh',15],
        ['cincinnati','s','knoxville',6],
        ['knoxville','s','atlanta',5],
        ['atlanta','ne','raleigh',7],
        ['atlanta','se','savannah',7],
        ['tampa','ne','jacksonville',4],
        ['tampa','se','miami',4],
        ['buffalo','se','new york',8],
        ['buffalo','s','pittsburgh',7],
        ['pittsburgh','se','washington dc',6],
        ['pittsburgh','s','raleigh',7],
        ['savannah','ne','raleigh',7],
        ['savannah','s','jacksonville',0],
        ['washington dc','ne','philadelphia',3],
        ['washington dc','se','norfolk',5],
        ['raleigh','ne','norfolk',3],
        ['philadelphia','ne','new york',0],
        ['new york','ne','boston',3]
    ],
    'automa_start_cities':{
        'e':'san francisco',
        'w':'norfolk',
        'n':'houston',
        's':'duluth',
        'ne':'san diego',
        'sw':'boston',
        'se': 'seattle',
        'nw': 'miami'
    }
}
plants = [
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

def random_direction():
    return random.choice(list(direction_lookup.keys()))


class ResourceRow:
    def __init__(self,kind,bins,per_bin,first_fill_amount,refill_amounts):
        self.costs = [1,2,3,4,5,6,7,8,10,12,14,16]
        self.first_fill_amount = first_fill_amount
        self.refill_amounts = refill_amounts
        self.refill_rates = [self.refill_amounts[0],self.refill_amounts[1],self.refill_amounts[2]]
        self.kind = kind
        self.bins = []
        for ii in range(0,bins):
            self.bins.append(0)
        self.index = bins-1
        self.bin_size = per_bin
        self.quantity = 0
        self.quantity_max = 12 if kind == 'nuke' else 24
        self.bin_count = bins
        filling = True
        while self.costs[self.index] >= self.first_fill_amount and filling:
            self.bins[self.index] = self.bin_size
            self.quantity += 1 if kind == 'nuke' else 3
            if not self.next_cheaper_bin_index():
                filling = False

    def next_cheaper_bin_index(self):
        if self.index > 0:
            self.index -= 1
            return True
        if self.index <= 0:
            self.index = 0
            return False

    def next_expensive_bin_index(self):
        if self.index < len(self.bins) - 1:
            self.index += 1
            return True
        if self.index >= len(self.bins):
            self.index = len(self.bins) - 1
            return False

    def take_one(self,money):
        if self.bins[self.index] == 0:
            if self.next_expensive_bin_index():
                if money >= self.costs[self.index]:
                    self.bins[self.index] -= 1
                    money -= self.costs[self.index]
                    self.quantity -= 1
                    return True,money
                else:
                    return False,money
            else:
                return False,money
        else:
            if money >= self.costs[self.index]:
                self.bins[self.index] -= 1
                money -= self.costs[self.index]
                self.quantity -= 1
                return True,money
            else:
                return False,money

    def put_one(self):
        if self.bins[self.index] >= self.bin_size:
            self.bins[self.index] = self.bin_size
            if self.next_cheaper_bin_index():
                self.bins[self.index] += 1
                self.quantity += 1
                return True
            else:
                return False
        else:
            self.bins[self.index] += 1
            self.quantity += 1
            return True


    def refill_phase(self,step_index):
        refill_rate = self.refill_rates[step_index]
        if refill_rate <= 0:
            return
        for ii in range(0,refill_rate):
            if self.quantity < self.quantity_max:
                self.put_one()

    def current_cost(self):
        return self.costs[self.index]

    def debug(self):
        debug_game(f'{self.bins}<-{self.kind} ({self.quantity})')

class ResourceMarket:
    def __init__(self,start_amounts,refill_rates):
        self.kinds = {
            'coal': 0,
            'oil': 1,
            'trash': 2,
            'nuke': 3
        }
        self.start_amounts = start_amounts
        self.refill_rates = refill_rates
        self.rows = [
            ResourceRow('coal',8,3,self.start_amounts[0],[self.refill_rates[0][0],self.refill_rates[1][0],self.refill_rates[2][0]]),
            ResourceRow('oil',8,3,self.start_amounts[1],[self.refill_rates[0][1],self.refill_rates[1][1],self.refill_rates[2][1]]),
            ResourceRow('trash',8,3,self.start_amounts[2],[self.refill_rates[0][2],self.refill_rates[1][2],self.refill_rates[2][2]]),
            ResourceRow('nuke',12,1,self.start_amounts[3],[self.refill_rates[0][3],self.refill_rates[1][3],self.refill_rates[2][3]])
        ]

    def purchase(self,kind,amount,money):
        resource_row = None
        if kind == 'wind':
            return True,money
        purchased = True
        taken = 0
        while purchased and taken < amount:
            if kind == 'oil/coal':
                resource_row = self.rows[0] if self.rows[0].current_cost() < self.rows[1].current_cost() else self.rows[1]
            else:
                resource_row = self.rows[self.kinds[kind]]
            purchased,money = resource_row.take_one(money)
            if purchased:
                taken += 1
        return purchased,money,taken

    def refill_phase(self,step):
        for row in self.rows:
            row.refill_phase(step - 1)

    def cost_to_buy(self,kind,amount):
        row_backup = deepcopy(self.rows[self.kinds[kind]])
        purchased,money,taken = self.purchase(kind,amount,10000)
        self.rows[self.kinds[kind]] = row_backup
        return 10000-money,taken

    def debug(self):
        for row in self.rows:
            row.debug()


class City:
    def __init__(self,zone,name,connections):
        self.zone = zone
        self.name = name
        self.connection_count = connections
        self.connections = {}
        self.added_connection_count = 0
        self.sites = []

    def build_cost(self,step,builder):
        if len(self.sites) == 0:
            return 10
        if step > 1 and len(self.sites) <= 1:
            if builder == 'human' and builder in self.sites:
                return 999
            return 15
        if step > 2 and len(self.sites) <= 2:
            if builder == 'human' and builder in self.sites:
                return 999
            return 20
        return 999

    def add_connection(self,connection):
        self.connections[connection.direction] = connection
        self.added_connection_count += 1

    def build_house(self,builder,step):
        cost = self.build_cost(step,builder)
        self.sites.append(builder)
        return cost

    def has_open_site(self,step):
        return len(self.sites) < step

    def get_connection(self,direction):
        if direction in self.connections:
            return self.connections[direction]
        return None

    def debug(self):
        debug_game(f"City {self.name} should have {self.connection_count} connections")
        debug_game("Connection list")
        for k,v in self.connections.items():
            v.debug()

class Connection:
    def __init__(self,direction,destination,cost):
        self.direction = direction
        self.destination = destination
        self.cost = int(cost)

    def debug(self):
        debug_game(f"  -> move {self.direction} to {self.destination} for {self.cost}")

class ConnectionPath:
    def __init__(self,first_city:City=None):
        self.cities = [first_city]
        self.city_lookup = {}
        self.city_lookup[first_city.name] = True
        self.cost = 0

    def length(self):
        return len(self.cities) - 1

    def add(self,city,cost):
        self.cities.append(city)
        self.cost += cost
        self.city_lookup[city.name] = True

    def tip(self):
        return self.cities[-1]

    def walked(self,city):
        return city.name in self.city_lookup

class GameMap:
    def __init__(self,definition:dict):
        self.definition = definition
        self.max_connections = 7
        self.city_lookup = {}
        for city in self.definition['cities']:
            self.city_lookup[city[1]] = City(city[0],city[1],city[2])
        for connection in self.definition['connections']:
            city = self.city_lookup[connection[0]]
            city.add_connection(Connection(connection[1],connection[2],connection[3]))
            self.city_lookup[connection[0]] = city
            city = self.city_lookup[connection[2]]
            city.add_connection(Connection(direction_lookup[connection[1]].opposite,connection[0],connection[3]))
            self.city_lookup[connection[2]] = city
        self.resource_market = ResourceMarket(self.definition['start_resources'],self.definition['refill'])
        self.automa_start_cities = definition['automa_start_cities']
        self.validate_cities()

    def validate_cities(self):
        for k,city in self.city_lookup.items():
            if city.connection_count != city.added_connection_count:
                print(f"City has mismatched connections")
                city.debug()
                import sys
                sys.exit(1)

    def walk_connections(self,direction,max_distance,step,connection_path,ignore_cities=None):
        if connection_path.length() >= max_distance or connection_path.tip().has_open_site(step):
            return [connection_path]
        results = []
        dir_check = 8
        direction = direction_lookup[direction].prev
        while dir_check > 0:
            direction = direction_lookup[direction].next
            city = connection_path.tip()
            connection = city.get_connection(direction)

            if connection != None:
                destination = self.city_lookup[connection.destination]
                if not connection_path.walked(destination) and (ignore_cities == None or not connection.destination in ignore_cities) :
                    connection_path.add(destination,connection.cost)
                    results += self.walk_connections(direction,max_distance,step,deepcopy(connection_path))
            dir_check -= 1
        return sorted(results,key=lambda xx: xx.cost)

    def first_automa_city(self,direction:str):
        city = self.automa_start_cities[direction.lower()]
        self.city_lookup[city].build_house('automa',1)
        return self.city_lookup[city]

    def next_automa_city(self,direction:str,build_target:City,step:int,ignore_cities:list):
        connection_paths = self.walk_connections(direction,self.max_connections,step,ConnectionPath(build_target),ignore_cities)
        if len(connection_paths) == 0:
            return None
        connection_paths[0].tip().build_house('automa',step)
        return connection_paths[0].tip()

    def first_human_city(self):
        direction = random_direction()
        connection_paths = self.walk_connections(direction,self.max_connections,1,ConnectionPath(self.city_lookup['kansas city']))
        return connection_paths[0].tip(),connection_paths[0].cost

    def next_human_city(self,direction,human_target,step):
        connection_paths = self.walk_connections(direction,self.max_connections,step,ConnectionPath(human_target))
        return connection_paths[0].tip(),connection_paths[0].cost

class Plant:
    def __init__(self,definition:dict):
        self.cost = definition[0]
        self.resource_amount = definition[1]
        self.resource_kind = definition[2]
        self.power_output = definition[3]
        self.is_step_3 = definition[2] == 'step3'

class PlantMarket:
    def __init__(self,cards):
        self.cards = cards
        self.market = [cards.pop(0),cards.pop(0),cards.pop(0),cards.pop(0),cards.pop(0),cards.pop(0),cards.pop(0),cards.pop(0)]
        self.step_3 = cards.pop()
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


class AutomaCard:
    def __init__(self,definition):
        self.definition = definition
        self.plant_auction = [definition['market1'],definition['market2'],definition['market3'],definition['market4']]
        self.ante = [definition['ante1'],definition['ante2'],definition['ante3'],definition['ante4']]
        self.resource_purchase = [definition['resource1'],definition['resource2'],definition['resource3'],definition['resource4']]
        self.city_build = [definition['build1'],definition['build2'],definition['build3'],definition['build4']]
        self.build_direction = definition['compass_direction']
        self.score = len([xx for xx in self.city_build if xx > 1])

class Automa:
    def __init__(self,cards):
        self.money = 10000 # Never updates, this just lets it claim plants at any cost
        self.deck = cards
        random.shuffle(self.deck)
        self.discard = []
        self.phase_cards = []
        self.auction_index = 0
        self.resource_index = 0
        self.build_index = 0
        self.plants = []
        self.resource_purchase_index = 3
        self.build_index = 3
        self.houses = 0
        self.build_target = None

    def debug(self):
        debug_game('=-Automa Debug-=')
        debug_game("  plants")
        debug_game(f"  {[f'#{x.cost} - {x.resource_kind} x {x.resource_amount}' for x in self.plants]}")

    def tiebreaker(self):
        # TODO Variant - Average of plants, not highest
        return self.plants[0].cost

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
        self.plants.append(plant)
        self.plants = sorted(self.plants,key=lambda xx: xx.cost,reverse=True)
        if len(self.plants) > 4:
            low_wind_index = -1
            for ii in range(0,len(self.plants)):
                if self.plants[ii].resource_kind == 'wind':
                    low_wind_index = ii
            if ii != -1:
                del self.plants[ii]
            else:
                self.plants = self.plants[0:4]

    def get_plant_auction_index(self):
        return self.phase_cards[0].plant_auction[self.auction_index]

    def get_current_ante(self):
        return self.phase_cards[0].ante[self.auction_index]

    def next_auction_index(self):
        self.auction_index += 1

    def reset_indices(self):
        self.auction_index = 0
        self.resource_purchase_index = 3
        self.build_index = 3

    def get_player_order(self,human_plant):
        human_order = 1
        for plant in self.plants:
            if plant.cost < human_plant.cost:
                return human_order
            human_order += 1
        return human_order

    def get_resource_purchase_mult(self):
        mult = self.phase_cards[1].resource_purchase[self.resource_purchase_index]
        self.resource_purchase_index -= 1
        return int(mult[0])

    def get_resource_purchase_plant(self):
        return self.plants[self.resource_purchase_index]

    def get_build_score(self):
        return self.phase_cards[2].score

    def build_houses(self,game_map,step):
        direction = self.phase_cards[2].build_direction.lower()
        debug_game(f"==Automa building {direction} of {self.build_target.name if self.build_target else 'center'} during step {step}")
        houses_to_place = self.phase_cards[2].city_build[self.build_index]
        built = 0
        true_last_city = None
        built_this_turn = []
        for ii in range(0,houses_to_place):
            debug_game(f'Automa placing house {ii+1} of {houses_to_place}')
            if self.houses == 0:
                self.build_target = game_map.first_automa_city(direction)
                debug_game(f'Automa first city is {self.build_target.name}')
                self.houses += 1
                built += 1
            else:
                last_city = game_map.next_automa_city(direction,self.build_target,step,built_this_turn)
                if last_city:
                    built_this_turn.append(last_city.name)
                    true_last_city = last_city
                    debug_game(f'Automa built in {last_city.name}')
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

    def debug(self):
        debug_game('=-Human-=')
        debug_game(f'  resources -> {self.resources}')
        debug_game(f'  money {self.money}')
        debug_game("  plants")
        debug_game([f'  #{x.cost} - {x.resource_kind} x {x.resource_amount}' for x in self.plants])

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
                debug_game(f"Wallet has ${self.money}. Requesting {-balance[order]} {order}")
                cost,amount = resource_market.cost_to_buy(order,-balance[order])
                if cost <= self.money:
                    purchased,post_money,taken = resource_market.purchase(order,-balance[order],self.money)
                    self.money = post_money
                    debug_game(f"Human bought {taken} {order}")
                    self.resources[order] += taken
                    filled_orders.append([order,taken,f'${cost}'])
                else:
                    debug_game(f"Human didn't have enough money for {-balance[order]} {order}")
        return filled_orders

    def build_houses(self,game_map,step):
        if self.houses == 0:
            destination,money = game_map.first_human_city()
            destination.build_house('player1',1)
            self.cities.append(destination)
            self.houses += 1
            return 1,10
        else:
            can_afford = True
            built = 0
            total_cost = 0
            while can_afford and self.houses < 15:
                destination = random.choice(self.cities)
                direction = random_direction()
                target,cost = game_map.next_human_city(direction,destination,step)
                if cost < self.money:
                    debug_game(f'Human building in {target.name} for ${cost}')
                    city_cost = target.build_house('player1',step)
                    self.cities.append(target)
                    self.houses += 1
                    self.money -= cost + city_cost
                    total_cost += cost + city_cost
                    built += 1
                else:
                    can_afford = False
            if built == 0:
                if self.houses >= 15:
                    debug_game(f'Human does not need to build any more houses')
                else:
                    debug_game(f'Human cannot afford to build this turn')
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
        debug_game(f'Human powered {powered} cities and made {power_payouts[powered]} money')
        self.money += power_payouts[powered]

    def power_capacity(self):
        return sum(x.power_output for x in self.plants)


def fresh_automa(automa_definitions):
    return Automa([AutomaCard(x) for x in automa_definitions])

def fresh_market():
    return PlantMarket([Plant(x) for x in plants])

def fresh_map():
    return GameMap(us_map)

def fresh_human():
    return Human()