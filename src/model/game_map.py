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
        if cost is None:
            return None
        self.sites.append(builder)
        return cost

    def has_open_site(self, step: int, builder: str):
        return self.build_cost(step, builder) is not None

    def get_connection(self, direction):
        return self.connections.get(direction)

    def debug(self):
        debug.game(f"City {self.name} should have {self.connection_count} connections")
        debug.game("Connection list")
        for key, conn in self.connections.items():
            conn.debug()

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

        region_choice = random.choice(self.definition["region_ids"])
        regions = [region_choice]
        shuffled_conns = list(self.definition["region_connections"])
        random.shuffle(shuffled_conns)
        for connection in shuffled_conns:
            if (
                connection[0] == region_choice
                and connection[1] not in regions
                and len(regions) < 3
            ):
                regions.append(connection[1])
            if (
                connection[1] == region_choice
                and connection[0] not in regions
                and len(regions) < 3
            ):
                regions.append(connection[0])
            if len(regions) == 3:
                break
        if len(regions) < 3 and len(regions) == 2:
            second_region = regions[1]
            for connection in shuffled_conns:
                if (
                    connection[0] == second_region
                    and connection[1] not in regions
                    and len(regions) < 3
                ):
                    regions.append(connection[1])
                if (
                    connection[1] == second_region
                    and connection[0] not in regions
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

        cities_to_ingest = [
            city for city in self.definition["cities"] if city[0] in regions
        ]
        debug.game(
            f"There are {len(cities_to_ingest) * 3} spaces to build cities. Only {len(cities_to_ingest)} are usable by the human"
        )
        debug.game(
            f"A player needs to build {self.step_2_city_count} for step 2 and {self.end_game_city_count} for the end game"
        )

        self.city_lookup = {
            city[1]: City(city[0], city[1], city[2]) for city in cities_to_ingest
        }

        for connection in self.definition["connections"]:
            if connection[0] in self.city_lookup and connection[2] in self.city_lookup:
                self.city_lookup[connection[0]].add_connection(
                    Connection(connection[1], connection[2], connection[3])
                )
                self.city_lookup[connection[2]].add_connection(
                    Connection(
                        model.get_direction(connection[1]).opposite,
                        connection[0],
                        connection[3],
                    )
                )
        self.automa_start_cities = definition["automa_start_cities"]

    def validate_cities(self):
        for key, city in self.city_lookup.items():
            if city.connection_count != city.added_connection_count:
                print("City has mismatched connections")
                city.debug()
                import sys

                sys.exit(1)

    def first_automa_city(self, direction: str, builder: str):
        target_name = self.automa_start_cities.get(direction)
        if target_name in self.city_lookup and self.city_lookup[
            target_name
        ].has_open_site(1, builder):
            city_node = self.city_lookup[target_name]
            return city_node, city_node.build_cost(1, builder)

        best_city = None
        lowest_dist = float("inf")
        if target_name and target_name in self.weights:
            for candidate_name, candidate_city in self.city_lookup.items():
                if candidate_city.has_open_site(1, builder):
                    dist = self.weights[target_name].get(candidate_name, float("inf"))
                    if dist < lowest_dist:
                        lowest_dist = dist
                        best_city = candidate_city
        if best_city:
            return best_city, best_city.build_cost(1, builder)

        for candidate_city in self.city_lookup.values():
            if candidate_city.has_open_site(1, builder):
                return candidate_city, candidate_city.build_cost(1, builder)
        return None, None

    def next_automa_city(
        self, direction: str, build_target: City, step: int, builder: str
    ):
        ordered_directions = []
        current_direction_key = model.get_direction(direction).prev
        for _ in range(8):
            current_direction_key = model.get_direction(current_direction_key).next
            ordered_directions.append(current_direction_key)

        for dir_key in ordered_directions:
            connection = build_target.get_connection(dir_key)
            if connection is not None and connection.destination in self.city_lookup:
                candidate = self.city_lookup[connection.destination]
                site_cost = candidate.build_cost(step, builder)
                if site_cost is not None:
                    return candidate, site_cost + connection.cost

        best_city = None
        lowest_total_cost = float("inf")
        city_weights = self.weights[build_target.name]
        for city_name, city in self.city_lookup.items():
            if city_name == build_target.name:
                continue
            site_cost = city.build_cost(step, builder)
            if site_cost is not None and city_name in city_weights:
                total_cost = city_weights[city_name] + site_cost
                if total_cost < lowest_total_cost:
                    lowest_total_cost = total_cost
                    best_city = city

        if best_city is not None:
            return best_city, lowest_total_cost
        return None, None

    def first_human_city(self):
        available_cities = [
            city for city in self.city_lookup.values() if city.has_open_site(1, "Human")
        ]
        if available_cities:
            chosen = random.choice(available_cities)
            return chosen, 10
        return None, None

    def next_human_city_from_network(self, wallet, owned_city_names, step):
        best_city = None
        lowest_total_cost = float("inf")
        for candidate_name, candidate_city in self.city_lookup.items():
            if candidate_name in owned_city_names:
                continue
            site_cost = candidate_city.build_cost(step, "Human")
            if site_cost is None:
                continue
            min_conn_cost = float("inf")
            for owned_name in owned_city_names:
                cost = self.weights[owned_name].get(candidate_name, float("inf"))
                if cost < min_conn_cost:
                    min_conn_cost = cost
            total_cost = min_conn_cost + site_cost
            if total_cost <= wallet and total_cost < lowest_total_cost:
                lowest_total_cost = total_cost
                best_city = candidate_city

        if best_city is not None:
            return best_city, lowest_total_cost
        return None, None

    def debug(self):
        debug.game("=-Game Map-=")
        for city_name, city in self.city_lookup.items():
            if len(city.sites) > 0:
                debug.game(f"{city_name} - {len(city.sites)} - {city.sites}")
