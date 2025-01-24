from copy import deepcopy
import random

import src.debug as debug
import src.model as model

class City:
    def __init__(self,zone,name,connections):
        self.zone = zone
        self.name = name
        self.connection_count = connections
        self.connections = {}
        self.added_connection_count = 0
        self.sites = []

    def add_connection(self,connection):
        self.connections[connection.direction] = connection
        self.added_connection_count += 1

    def build_cost(self,step:int,builder:str):
        if builder in self.sites:
            return None
        if len(self.sites) < 1:
            return 10
        if step > 1 and len(self.sites) < 2:
            return 15
        if step > 2 and len(self.sites) < 3:
            return 20
        return None

    def build_house(self,step:int,builder:str):
        cost = self.build_cost(step,builder)
        if cost == None:
            return cost
        self.sites.append(builder)
        return cost

    def has_open_site(self,step:int,builder:str):
        return self.build_cost(step,builder) != None

    def get_connection(self,direction):
        if direction in self.connections:
            return self.connections[direction]
        return None

    def debug(self):
        debug.game(f"City {self.name} should have {self.connection_count} connections")
        debug.game("Connection list")
        for k,v in self.connections.items():
            v.debug()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.name} - ({self.sites})'

class Connection:
    def __init__(self,direction,destination,cost):
        self.direction = direction
        self.destination = destination
        self.cost = int(cost)

    def debug(self):
        debug.game(f"  -> move {self.direction} to {self.destination} for {self.cost}")

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

    def tip_cost(self,step:int,builder:str):
        build_cost = self.tip().build_cost(step,builder)
        if build_cost == None:
            return None
        return self.cost + build_cost

    def walked(self,city):
        return city.name in self.city_lookup

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.cost} - {self.cities}'

class GameMap:
    def __init__(self,definition:dict,player_count):
        self.definition = definition

        self.player_info = self.definition['player_count_info'][player_count-2]
        self.resource_market = model.ResourceMarket(self.definition['start_resources'],self.player_info[-1])
        self.regions_used = self.player_info[0]
        self.plants_removed = self.player_info[1]
        self.plants_per_player = self.player_info[2]
        self.step_2_city_count = self.player_info[3]
        self.end_game_city_count = self.player_info[4]

        cities_to_ingest = []
        region = random.choice(self.definition['region_ids'])
        regions = [region]
        random.shuffle(self.definition['region_connections'])
        for connection in self.definition['region_connections']:
            if connection[0] == region and not connection[1] in regions and len(regions) < 3:
                regions.append(connection[1])
            if connection[1] == region and not connection[0] in regions and len(regions) < 3:
                regions.append(connection[0])
            if len(regions) == 3:
                break
        if len(regions) == 2:
            region = regions[1]
            for connection in self.definition['region_connections']:
                if connection[0] == region and not connection[1] in regions and len(regions) < 3:
                    regions.append(connection[1])
                if connection[1] == region and not connection[0] in regions and len(regions) < 3:
                    regions.append(connection[0])
                if len(regions) == 3:
                    break
        debug.game(f'Using regions {regions}')
        if len(regions) < self.regions_used:
            print("An error occurred while picking regions")
            print(regions)
            import sys
            sys.exit(1)
        for city in self.definition['cities']:
            if city[0] in regions:
                cities_to_ingest.append(city)
        debug.game(f'There are {len(cities_to_ingest) * 3} spaces to build cities. Only {len(cities_to_ingest)} are usable by the human')
        debug.game(f'A player needs to build {self.step_2_city_count} for step 2 and {self.end_game_city_count} for the end game')

        self.city_lookup = {}
        for city in cities_to_ingest:
            self.city_lookup[city[1]] = City(city[0],city[1],city[2])
        for connection in self.definition['connections']:
            # This should only happen if the connection is to a region that is excluded by player count
            if not connection[0] in self.city_lookup or not connection[2] in self.city_lookup:
                continue
            city = self.city_lookup[connection[0]]
            city.add_connection(Connection(connection[1],connection[2],connection[3]))
            self.city_lookup[connection[0]] = city
            city = self.city_lookup[connection[2]]
            city.add_connection(Connection(model.get_direction(connection[1]).opposite,connection[0],connection[3]))
            self.city_lookup[connection[2]] = city
        self.automa_start_cities = definition['automa_start_cities']
        #self.validate_cities() -- This doesn't work in < max regions

    def validate_cities(self):
        for k,city in self.city_lookup.items():
            if city.connection_count != city.added_connection_count:
                print(f"City has mismatched connections")
                city.debug()
                import sys
                sys.exit(1)

    def walk_connections(self,wallet,builder,direction,step,connection_path):
        if connection_path.tip().has_open_site(step,builder):
            return [connection_path]
        results = []
        dir_check = 8
        direction = model.get_direction(direction).prev
        while dir_check > 0:
            direction = model.get_direction(direction).next
            city = connection_path.tip()
            connection = city.get_connection(direction)
            if connection != None:
                destination = self.city_lookup[connection.destination]
                if not connection_path.walked(destination):
                    connection_path.add(destination,connection.cost)
                    results += self.walk_connections(wallet,builder,direction,step,deepcopy(connection_path))
            dir_check -= 1
        return sorted([yy for yy in results if yy != None],key=lambda xx: xx.tip_cost(step,builder))

    def first_automa_city(self,direction:str,builder:str):
        # TODO Have the automa handle per-region starting cities
        city_names = list(self.city_lookup.keys())
        random.shuffle(city_names)
        while True:
            random_city = self.city_lookup[city_names.pop()]
            if len(random_city.sites) == 0:
                build_cost = random_city.build_cost(1,builder)
                return random_city,build_cost

    def next_automa_city(self,direction:str,build_target:City,step:int,builder:str):
        connection_paths = self.walk_connections(None,builder,direction,step,ConnectionPath(build_target))
        if len(connection_paths) == 0:
            return None,None
        build_cost = connection_paths[0].tip().build_cost(step,builder)
        if build_cost == None:
            return None,None
        return self.city_lookup[connection_paths[0].tip().name],build_cost

    def first_human_city(self):
        city_names = list(self.city_lookup.keys())
        random.shuffle(city_names)
        while True:
            random_city = self.city_lookup[city_names.pop()]
            if len(random_city.sites) == 0:
                return random_city,10

    def next_human_city(self,wallet,direction,human_target,step):
        connection_paths = self.walk_connections(wallet,'Human',direction,step,ConnectionPath(human_target))
        if len(connection_paths) == 0:
            return None,None
        build_cost = connection_paths[0].tip_cost(step,'Human')
        if build_cost == None:
            return None,None
        return self.city_lookup[connection_paths[0].tip().name],build_cost

    def debug(self):
        debug.game('=-Game Map-=')
        for city_name,city in self.city_lookup.items():
            if len(city.sites) > 0:
                debug.game(f'{city_name} - {len(city.sites)} - {city.sites}')
