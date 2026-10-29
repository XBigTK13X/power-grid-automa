import random

import src.debug as debug
import src.model as model


class City:
    def __init__(self, zone, name, connections):
        self.zone = zone
        self.name = name
        self.connection_count = connections
        self.connections = {}
        self.added_connection_count = 0
        self.sites = []

    def add_connection(self, connection):
        self.connections[connection.direction] = connection
        self.added_connection_count += 1

    def build_cost(self, step: int, builder: str):
        if builder in self.sites:
            return None
        if len(self.sites) < 1:
            return 10
        if step > 1 and len(self.sites) < 2:
            return 15
        if step > 2 and len(self.sites) < 3:
            return 20
        return None

    def build_house(self, step: int, builder: str):
        cost = self.build_cost(step, builder)
        if cost == None:
            return cost
        self.sites.append(builder)
        return cost

    def has_open_site(self, step: int, builder: str):
        return self.build_cost(step, builder) != None

    def get_connection(self, direction):
        if direction in self.connections:
            return self.connections[direction]
        return None

    def debug(self):
        debug.game(f"City {self.name} should have {self.connection_count} connections")
        debug.game("Connection list")
        for k, v in self.connections.items():
            v.debug()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.name} - ({self.sites})"


class Connection:
    def __init__(self, direction, destination, cost):
        self.direction = direction
        self.destination = destination
        self.cost = int(cost)

    def debug(self):
        debug.game(f"  -> move {self.direction} to {self.destination} for {self.cost}")


class GameMap:
    def __init__(self, definition: dict, player_count):
        self.definition = definition
        self.weights = definition["weights"]

        self.player_info = self.definition["player_count_info"][player_count - 2]
        self.resource_market = model.ResourceMarket(
            self.definition["start_resources"], self.player_info[-1]
        )
        self.regions_used = self.player_info[0]
        self.plants_removed = self.player_info[1]
        self.plants_per_player = self.player_info[2]
        self.step_2_city_count = self.player_info[3]
        self.end_game_city_count = self.player_info[4]

        cities_to_ingest = []
        region = random.choice(self.definition["region_ids"])
        regions = [region]
        random.shuffle(self.definition["region_connections"])
        for connection in self.definition["region_connections"]:
            if (
                connection[0] == region
                and not connection[1] in regions
                and len(regions) < 3
            ):
                regions.append(connection[1])
            if (
                connection[1] == region
                and not connection[0] in regions
                and len(regions) < 3
            ):
                regions.append(connection[0])
            if len(regions) == 3:
                break
        if len(regions) == 2:
            region = regions[1]
            for connection in self.definition["region_connections"]:
                if (
                    connection[0] == region
                    and not connection[1] in regions
                    and len(regions) < 3
                ):
                    regions.append(connection[1])
                if (
                    connection[1] == region
                    and not connection[0] in regions
                    and len(regions) < 3
                ):
                    regions.append(connection[0])
                if len(regions) == 3:
                    break
        debug.game(f"Using regions {regions}")
        if len(regions) < self.regions_used:
            print("An error occurred while picking regions")
            print(regions)
            import sys

            sys.exit(1)
        for city in self.definition["cities"]:
            if city[0] in regions:
                cities_to_ingest.append(city)
        debug.game(
            f"There are {len(cities_to_ingest) * 3} spaces to build cities. Only {len(cities_to_ingest)} are usable by the human"
        )
        debug.game(
            f"A player needs to build {self.step_2_city_count} for step 2 and {self.end_game_city_count} for the end game"
        )

        self.city_lookup = {}
        for city in cities_to_ingest:
            self.city_lookup[city[1]] = City(city[0], city[1], city[2])
        for connection in self.definition["connections"]:
            if (
                not connection[0] in self.city_lookup
                or not connection[2] in self.city_lookup
            ):
                continue
            city = self.city_lookup[connection[0]]
            city.add_connection(Connection(connection[1], connection[2], connection[3]))
            self.city_lookup[connection[0]] = city
            city = self.city_lookup[connection[2]]
            city.add_connection(
                Connection(
                    model.get_direction(connection[1]).opposite,
                    connection[0],
                    connection[3],
                )
            )
            self.city_lookup[connection[2]] = city
        self.automa_start_cities = definition["automa_start_cities"]

    def validate_cities(self):
        for k, city in self.city_lookup.items():
            if city.connection_count != city.added_connection_count:
                print("City has mismatched connections")
                city.debug()
                import sys

                sys.exit(1)

    def first_automa_city(self, direction: str, builder: str):
        city_names = list(self.city_lookup.keys())
        random.shuffle(city_names)
        while len(city_names) > 0:
            random_city = self.city_lookup[city_names.pop()]
            if len(random_city.sites) == 0:
                build_cost = random_city.build_cost(1, builder)
                return random_city, build_cost
        return None, None

    def next_automa_city(
        self, direction: str, build_target: City, step: int, builder: str
    ):
        # 1. Automa checks directly connected neighbors in directional order
        ordered_directions = []
        current_direction_key = model.get_direction(direction).prev
        for ii in range(0, 8):
            current_direction_key = model.get_direction(current_direction_key).next
            ordered_directions.append(current_direction_key)

        for dir_key in ordered_directions:
            connection = build_target.get_connection(dir_key)
            if connection != None and connection.destination in self.city_lookup:
                candidate = self.city_lookup[connection.destination]
                site_cost = candidate.build_cost(step, builder)
                if site_cost != None:
                    return candidate, site_cost + connection.cost

        # 2. If all direct neighbors are full/unusable, pick closest valid city via precomputed weights
        best_city = None
        lowest_total_cost = float("inf")
        city_weights = self.weights[build_target.name]

        for city_name, city in self.city_lookup.items():
            if city_name == build_target.name:
                continue
            site_cost = city.build_cost(step, builder)
            if site_cost != None and city_name in city_weights:
                total_cost = city_weights[city_name] + site_cost
                if total_cost < lowest_total_cost:
                    lowest_total_cost = total_cost
                    best_city = city

        if best_city != None:
            return best_city, lowest_total_cost
        return None, None

    def first_human_city(self):
        city_names = list(self.city_lookup.keys())
        random.shuffle(city_names)
        while len(city_names) > 0:
            random_city = self.city_lookup[city_names.pop()]
            if len(random_city.sites) == 0:
                return random_city, 10
        return None, None

    def next_human_city(self, wallet, direction, human_target, step):
        best_city = None
        lowest_total_cost = float("inf")
        city_weights = self.weights[human_target.name]

        for city_name, city in self.city_lookup.items():
            if city_name == human_target.name:
                continue
            site_cost = city.build_cost(step, "Human")
            if site_cost != None and city_name in city_weights:
                total_cost = city_weights[city_name] + site_cost
                if total_cost <= wallet and total_cost < lowest_total_cost:
                    lowest_total_cost = total_cost
                    best_city = city

        if best_city != None:
            return best_city, lowest_total_cost
        return None, None

    def debug(self):
        debug.game("=-Game Map-=")
        for city_name, city in self.city_lookup.items():
            if len(city.sites) > 0:
                debug.game(f"{city_name} - {len(city.sites)} - {city.sites}")
