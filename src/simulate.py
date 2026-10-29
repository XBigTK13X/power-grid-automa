import sys
from statistics import mean, median

import src.debug as debug
import src.model as model
import src.plant_deck as plant_deck


class SimulatedGame:
    def __init__(self, player_count, map_data, cards):
        debug.sim("Setting up a new game")
        self.player_count = player_count
        self.game_map = model.GameMap(map_data, player_count)
        self.plant_market = model.PlantMarket(
            plant_deck.base_game_plants, self.game_map.plants_removed
        )
        self.automa = model.Automa(cards)
        self.human = model.Human()

        self.turn_count = 0
        self.first_turn = True
        self.step = 1
        start_resource_amounts = self.game_map.resource_market.amounts()
        self.resource_purchase_tracker = {
            "coal": {"human": 0, "automa": 0, "refill": start_resource_amounts[0]},
            "oil": {"human": 0, "automa": 0, "refill": start_resource_amounts[1]},
            "trash": {"human": 0, "automa": 0, "refill": start_resource_amounts[2]},
            "nuke": {"human": 0, "automa": 0, "refill": start_resource_amounts[3]},
        }
        self.automa_left_player_order = 0
        self.automa_right_player_order = 2
        self.human_player_order = 1

        self.automa_left_cities_built = 0
        self.automa_right_cities_built = 0
        self.human_cities_built = 0

    def game_is_over(self):
        return (
            self.automa_left_cities_built >= self.game_map.end_game_city_count
            or self.automa_right_cities_built >= self.game_map.end_game_city_count
            or self.human_cities_built >= self.game_map.end_game_city_count
        )

    def play(self):
        debug.sim("Entering sim loop")
        while not self.game_is_over():
            debug.sim(
                f"\n\n\n=-=-=-=-TURN {self.turn_count + 1} - Step {self.step}-=-=-=-="
            )
            if self.turn_count > 20:
                print("An error occurred during simulation.")
                print("The game will never take more than 20 turns")
                return None

            self.automa.draw_cards()
            if self.first_turn:
                while self.automa.has_market_skips():
                    self.automa.draw_cards()

            if not self.first_turn:
                self.phase_1_player_order()
            self.phase_2_plant_auction()
            if self.first_turn:
                self.phase_1_player_order()
                debug.sim(
                    f"Human's first turn player order is {self.human_player_order}"
                )
                self.first_turn = False

            self.phase_3_purchase_resources()
            self.phase_4_build_houses()
            self.phase_5_bureaucracy()

    def phase_1_player_order(self):
        debug.sim("\n - Phase 1 - Player Order")
        human_plant_cost = self.human.plants[-1].cost if self.human.plants else 0
        left_plant_cost = (
            self.automa.left_player.plant_stack[0].cost
            if self.automa.left_player.plant_stack
            else 0
        )
        right_plant_cost = (
            self.automa.right_player.plant_stack[0].cost
            if self.automa.right_player.plant_stack
            else 0
        )

        player_order_sort = sorted(
            [
                {
                    "name": "human",
                    "score": self.human_cities_built,
                    "plant": human_plant_cost,
                },
                {
                    "name": "automa_left",
                    "score": self.automa_left_cities_built,
                    "plant": left_plant_cost,
                },
                {
                    "name": "automa_right",
                    "score": self.automa_right_cities_built,
                    "plant": right_plant_cost,
                },
            ],
            key=lambda xx: (xx["score"], xx["plant"]),
            reverse=True,
        )
        for order_idx in range(len(player_order_sort)):
            entry = player_order_sort[order_idx]
            if entry["name"] == "human":
                self.human_player_order = order_idx
            elif entry["name"] == "automa_left":
                self.automa_left_player_order = order_idx
            elif entry["name"] == "automa_right":
                self.automa_right_player_order = order_idx

        debug.sim(
            f"Human is player {self.human_player_order} starting with ${self.human.money}"
        )
        debug.sim(f"AutomaLeft is player {self.automa_left_player_order} ")
        debug.sim(f"AutomaRight is player {self.automa_right_player_order}")

    def phase_2_plant_auction(self):
        debug.sim("\n - Phase 2 - Power Plant Auction")
        plants_sold = 0

        if self.first_turn:
            left_choice = self.automa.get_plant_auction_index(model.LEFT_SIDE)
            left_idx = left_choice - 1
            if 0 <= left_idx < len(self.plant_market.market):
                left_plant = self.plant_market.take_plant(left_idx)
                debug.sim(f"AutomaLeft purchased plant {left_plant.cost}")
                debug.sim(
                    f"AutomaLeft plant powers {left_plant.power_output} city for {left_plant.resource_amount} {left_plant.resource_kind}"
                )
                self.automa.claim_plant(left_plant, model.LEFT_SIDE)
                plants_sold += 1
                if self.plant_market.refill():
                    self.step = 3

            actual_plants = self.plant_market.get_actual_market()
            best_starting_plant = max(
                actual_plants, key=lambda xx: (xx.power_output, -xx.cost)
            )
            plant_idx = self.plant_market.market.index(best_starting_plant)
            human_plant = self.plant_market.take_plant(plant_idx)
            self.human.purchase_plant(
                self.plant_market, human_plant, 0, can_ignore=False
            )
            debug.sim(f"Human bought plant {human_plant.cost} for ${human_plant.cost}")
            debug.sim(
                f"Human plant powers {human_plant.power_output} city for {human_plant.resource_amount} {human_plant.resource_kind}"
            )
            plants_sold += 1
            if self.plant_market.refill():
                self.step = 3

            right_choice = self.automa.get_plant_auction_index(model.RIGHT_SIDE)
            right_idx = right_choice - 1
            if 0 <= right_idx < len(self.plant_market.market):
                right_plant = self.plant_market.take_plant(right_idx)
                debug.sim(f"AutomaRight purchased plant {right_plant.cost}")
                debug.sim(
                    f"AutomaRight plant powers {right_plant.power_output} city for {right_plant.resource_amount} {right_plant.resource_kind}"
                )
                self.automa.claim_plant(right_plant, model.RIGHT_SIDE)
                plants_sold += 1
                if self.plant_market.refill():
                    self.step = 3
            return

        human_purchased = False
        has_acted = []
        for action_index in range(self.player_count):
            if self.plant_market.is_empty():
                continue
            ante = self.automa.get_current_ante(has_acted)

            if action_index == self.human_player_order:
                if not human_purchased:
                    chosen_plant = self.human.choose_plant_to_auction(
                        self.plant_market, ante
                    )
                    if chosen_plant is not None:
                        plant_idx = self.plant_market.market.index(chosen_plant)
                        taken_plant = self.plant_market.take_plant(plant_idx)
                        if self.human.purchase_plant(
                            self.plant_market, taken_plant, ante, can_ignore=False
                        ):
                            human_purchased = True
                            plants_sold += 1
                            debug.sim(
                                f"Human bought plant {taken_plant.cost} for ${taken_plant.cost + ante}"
                            )
                            debug.sim(
                                f"Human plant powers {taken_plant.power_output} city for {taken_plant.resource_amount} {taken_plant.resource_kind}"
                            )
                            if self.plant_market.refill():
                                self.step = 3
                        else:
                            self.plant_market.replace(taken_plant)
                    else:
                        debug.sim("The human chose not to start an auction")
            else:
                automa_side = (
                    model.LEFT_SIDE
                    if action_index == self.automa_left_player_order
                    else model.RIGHT_SIDE
                )
                has_acted.append(automa_side)

                if self.step == 3 and len(self.plant_market.market) <= 3:
                    continue

                card_choice = self.automa.get_plant_auction_index(automa_side)
                if card_choice <= 0:
                    continue

                target_idx = card_choice - 1
                actual_market_limit = 6 if self.step == 3 else 4
                if target_idx >= actual_market_limit or not self.plant_market.has_plant(
                    target_idx
                ):
                    continue

                target_plant = self.plant_market.market[target_idx]
                if not human_purchased and self.human.wants_plant(
                    target_plant, ante, can_ignore=True
                ):
                    next_plant = self.plant_market.take_plant(target_idx)
                    self.human.purchase_plant(
                        self.plant_market, next_plant, ante, can_ignore=False
                    )
                    debug.sim(
                        f"Human outbid automa for plant {next_plant.cost} (powers {next_plant.power_output})"
                    )
                    human_purchased = True
                    plants_sold += 1
                else:
                    next_plant = self.plant_market.take_plant(target_idx)
                    automa_name = (
                        "AutomaLeft"
                        if automa_side == model.LEFT_SIDE
                        else "AutomaRight"
                    )
                    debug.sim(f"{automa_name} purchased plant {next_plant.cost}")
                    debug.sim(
                        f"{automa_name} plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}"
                    )
                    self.automa.claim_plant(next_plant, automa_side)
                    plants_sold += 1

                if self.plant_market.refill():
                    self.step = 3

        if plants_sold == 0 and not self.plant_market.is_empty():
            self.plant_market.remove_lowest()
            if self.plant_market.refill():
                self.step = 3

        human_purchased = False
        has_acted = []
        for action_index in range(self.player_count):
            if self.plant_market.is_empty():
                continue
            ante = self.automa.get_current_ante(has_acted)

            if action_index == self.human_player_order:
                if not human_purchased:
                    candidate_plant = self.plant_market.random()
                    if candidate_plant is not None:
                        if self.human.purchase_plant(
                            self.plant_market, candidate_plant, ante, can_ignore=True
                        ):
                            human_purchased = True
                            plants_sold += 1
                            debug.sim(
                                f"Human bought plant {candidate_plant.cost} for ${candidate_plant.cost + ante}"
                            )
                            debug.sim(
                                f"Human plant powers {candidate_plant.power_output} city for {candidate_plant.resource_amount} {candidate_plant.resource_kind}"
                            )
                            if self.plant_market.refill():
                                self.step = 3
                        else:
                            debug.sim("The human did not purchase a plant")
                            self.plant_market.replace(candidate_plant)
            else:
                automa_side = (
                    model.LEFT_SIDE
                    if action_index == self.automa_left_player_order
                    else model.RIGHT_SIDE
                )
                automa_name = (
                    "AutomaLeft" if automa_side == model.LEFT_SIDE else "AutomaRight"
                )
                has_acted.append(automa_side)

                if self.step == 3 and len(self.plant_market.market) <= 3:
                    continue

                card_choice = self.automa.get_plant_auction_index(automa_side)
                if card_choice <= 0:
                    continue

                target_idx = card_choice - 1
                actual_market_limit = 6 if self.step == 3 else 4
                if target_idx >= actual_market_limit or not self.plant_market.has_plant(
                    target_idx
                ):
                    continue

                next_plant = self.plant_market.take_plant(target_idx)
                if human_purchased or not self.human.purchase_plant(
                    self.plant_market, next_plant, ante, can_ignore=True
                ):
                    debug.sim(f"{automa_name} purchased plant {next_plant.cost}")
                    debug.sim(
                        f"{automa_name} plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}"
                    )
                    self.automa.claim_plant(next_plant, automa_side)
                    plants_sold += 1
                else:
                    debug.sim(
                        f"Human purchased plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}"
                    )
                    human_purchased = True
                    plants_sold += 1

                if self.plant_market.refill():
                    self.step = 3

        if plants_sold == 0 and not self.plant_market.is_empty():
            self.plant_market.remove_lowest()
            if self.plant_market.refill():
                self.step = 3

    def phase_3_purchase_resources(self):
        debug.sim("\n - Phase 3 - Purchase Resources")
        self.game_map.resource_market.debug()
        for ii in range(self.player_count):
            action_index = self.player_count - ii - 1
            if self.human_player_order == action_index:
                filled_orders = self.human.purchase_resources(
                    self.game_map.resource_market
                )
                for filled in filled_orders:
                    self.resource_purchase_tracker[filled[0]]["human"] += filled[1]
                debug.sim(f"Human filled resource orders {filled_orders}")
            else:
                automa_side = (
                    model.LEFT_SIDE
                    if action_index == self.automa_left_player_order
                    else model.RIGHT_SIDE
                )
                automa_name = (
                    "AutomaLeft" if automa_side == model.LEFT_SIDE else "AutomaRight"
                )
                for active_plant in self.automa.get_resource_purchase_plants(
                    automa_side
                ):
                    resource_amount = active_plant.resource_amount
                    if active_plant.resource_kind != "wind":
                        if active_plant.resource_kind == "oil/coal":
                            start_amounts = self.game_map.resource_market.amounts()
                            purchased, money, taken = (
                                self.game_map.resource_market.purchase(
                                    "oil/coal", resource_amount, 10000
                                )
                            )
                            debug.sim(
                                f"{automa_name} took {taken} {active_plant.resource_kind} from the resource market"
                            )
                            end_amounts = self.game_map.resource_market.amounts()
                            coal_taken = start_amounts[0] - end_amounts[0]
                            oil_taken = start_amounts[1] - end_amounts[1]
                            self.resource_purchase_tracker["coal"]["automa"] += (
                                coal_taken
                            )
                            self.resource_purchase_tracker["oil"]["automa"] += oil_taken
                        else:
                            purchased, money, taken = (
                                self.game_map.resource_market.purchase(
                                    active_plant.resource_kind, resource_amount, 10000
                                )
                            )
                            self.resource_purchase_tracker[active_plant.resource_kind][
                                "automa"
                            ] += taken
                            debug.sim(
                                f"{automa_name} took {taken} {active_plant.resource_kind} from the resource market"
                            )
        debug.sim("Ending resource market")
        self.game_map.resource_market.debug()

    def phase_4_build_houses(self):
        debug.sim("\n - Phase 4 - Build Cities")
        for ii in range(self.player_count):
            action_index = self.player_count - ii - 1
            if self.human_player_order == action_index:
                debug.sim("Human's turn to build houses")
                built, cost = self.human.build_houses(self.game_map, self.step)
                if built is None:
                    debug.sim("Human unable to find a free space!")
                else:
                    self.human_cities_built += built
                    debug.sim(f"Human built {built} houses for ${cost}")
            else:
                automa_side = (
                    model.LEFT_SIDE
                    if action_index == self.automa_left_player_order
                    else model.RIGHT_SIDE
                )
                automa_name = (
                    "AutomaLeft" if automa_side == model.LEFT_SIDE else "AutomaRight"
                )
                debug.sim(f"{automa_name} turn to build houses")
                built = self.automa.build_houses(self.game_map, self.step, automa_side)
                if built is None:
                    debug.sim(f"{automa_name} unable to build any houses")
                else:
                    debug.sim(f"{automa_name} built {built} houses")

                if automa_side == model.LEFT_SIDE:
                    self.automa_left_cities_built = self.automa.left_player.houses
                else:
                    self.automa_right_cities_built = self.automa.right_player.houses

            max_cities = max(
                self.human_cities_built,
                self.automa_left_cities_built,
                self.automa_right_cities_built,
            )
            while (
                self.plant_market.market
                and self.plant_market.market[0].cost <= max_cities
            ):
                self.plant_market.remove_lowest()
                if self.plant_market.refill():
                    self.step = 3

    def phase_5_bureaucracy(self):
        debug.sim("\n - Phase 5 - Bureaucracy")
        self.automa_left_cities_built = self.automa.left_player.houses
        self.automa_right_cities_built = self.automa.right_player.houses
        self.human_cities_built = self.human.houses

        if self.step == 1:
            if (
                self.automa_left_cities_built >= self.game_map.step_2_city_count
                or self.automa_right_cities_built >= self.game_map.step_2_city_count
                or self.human_cities_built >= self.game_map.step_2_city_count
            ):
                self.step = 2
                self.plant_market.remove_lowest()
                if self.plant_market.refill():
                    self.step = 3

        if not self.game_is_over():
            refill_amounts = self.game_map.resource_market.refill_phase(self.step)
            for kind, amount in refill_amounts.items():
                self.resource_purchase_tracker[kind]["refill"] += amount
            self.human.power_cities()

            if self.step in [1, 2]:
                if self.plant_market.cycle_highest():
                    self.step = 3
            elif self.step == 3:
                self.plant_market.remove_lowest()
                self.plant_market.refill()

        self.turn_count += 1
        debug.sim(f"Finished turn {self.turn_count} on step {self.step}")
        debug.sim(f"automa left score {self.automa_left_cities_built}")
        debug.sim(f"automa right score {self.automa_right_cities_built}")
        debug.sim(f"human score {self.human_cities_built}")
        self.automa.debug()
        self.human.debug()
        self.game_map.debug()

    def document_result(self):
        debug.sim(f"Automa left score {self.automa_left_cities_built}")
        debug.sim(f"Automa right score {self.automa_right_cities_built}")
        debug.sim(
            f"Human score {self.human_cities_built} cities and power {self.human.power_capacity()}"
        )
        debug.sim(
            f"Left automa built {self.automa_left_cities_built} , right automa built {self.automa_right_cities_built}, and human built {self.human_cities_built}"
        )
        result = model.GameResult()
        result.turns_taken = self.turn_count

        result.human_money = self.human.money
        result.human_power_capacity = self.human.power_capacity()
        result.human_cities_built = self.human_cities_built
        result.left_cities_built = self.automa_left_cities_built
        result.right_cities_built = self.automa_right_cities_built

        result.automa_tiebreaker = self.automa.tiebreaker()
        result.human_plants = [xx.cost for xx in self.human.plants]
        result.left_plants = [[xx.cost for xx in self.automa.left_player.plant_stack]]
        result.right_plants = [[xx.cost for xx in self.automa.right_player.plant_stack]]

        result.resource_purchase_tracker = self.resource_purchase_tracker
        result.resource_market = self.game_map.resource_market

        result.human_win = result.calculate_winner()
        debug.sim(f"The game took {self.turn_count} turns")
        return result


def play_game(cards, map_data, player_count):
    simulated_match = SimulatedGame(player_count, map_data, cards)
    simulated_match.play()
    return simulated_match.document_result()


def play_games(cards, amount, map_data, player_count):
    tallies = {"human": 0, "automa_left": 0, "automa_right": 0}
    results = []

    metrics = {
        "turns": [],
        "human_money": [],
        "human_cities": [],
        "left_cities": [],
        "right_cities": [],
        "human_power_capacity": [],
        "automa_city_wins": 0,
        "human_city_wins": 0,
        "automa_tiebreaker_wins": 0,
        "human_tiebreaker_wins": 0,
        "end_resources": [0, 0, 0, 0],
        "consumed_resources": {
            "coal": {"human": 0, "automa": 0},
            "oil": {"human": 0, "automa": 0},
            "trash": {"human": 0, "automa": 0},
            "nuke": {"human": 0, "automa": 0},
        },
        "outliers": {
            "long_games": [],
            "short_games": [],
            "unpowered_endgame": [],
            "low_cash_human": [],
            "tiebreakers": [],
        },
    }

    for ii in range(amount):
        if amount > 1:
            sys.stdout.write(f"\rGame {ii + 1}/{amount}")
            sys.stdout.flush()

        game_result = play_game(cards, map_data, player_count)
        debug.flush(ii)
        results.append(game_result)

        if game_result.human_win:
            tallies["human"] += 1
        elif game_result.left_cities_built >= game_result.right_cities_built:
            tallies["automa_left"] += 1
        else:
            tallies["automa_right"] += 1

        metrics["turns"].append(game_result.turns_taken)
        metrics["human_money"].append(game_result.human_money)
        metrics["human_cities"].append(game_result.human_cities_built)
        metrics["left_cities"].append(game_result.left_cities_built)
        metrics["right_cities"].append(game_result.right_cities_built)
        metrics["human_power_capacity"].append(game_result.human_power_capacity)

        if game_result.automa_city_win:
            metrics["automa_city_wins"] += 1
        if game_result.human_city_win:
            metrics["human_city_wins"] += 1
        if game_result.automa_tiebreaker_win:
            metrics["automa_tiebreaker_wins"] += 1
        if game_result.human_tiebreaker_win:
            metrics["human_tiebreaker_wins"] += 1

        if game_result.turns_taken >= 15:
            metrics["outliers"]["long_games"].append(ii)
        elif game_result.turns_taken <= 9:
            metrics["outliers"]["short_games"].append(ii)

        if game_result.human_power_capacity < game_result.human_cities_built:
            metrics["outliers"]["unpowered_endgame"].append(ii)

        if game_result.human_money <= 5:
            metrics["outliers"]["low_cash_human"].append(ii)

        if game_result.automa_tiebreaker_win or game_result.human_tiebreaker_win:
            metrics["outliers"]["tiebreakers"].append(ii)

        for row_index in range(4):
            metrics["end_resources"][row_index] += game_result.resource_market.rows[
                row_index
            ].quantity

        for kind in ["coal", "oil", "trash", "nuke"]:
            metrics["consumed_resources"][kind]["human"] += (
                game_result.resource_purchase_tracker[kind]["human"]
            )
            metrics["consumed_resources"][kind]["automa"] += (
                game_result.resource_purchase_tracker[kind]["automa"]
            )

    if amount > 1:
        sys.stdout.write("\n")
        sys.stdout.flush()

    automa_total_wins = tallies["automa_left"] + tallies["automa_right"]
    automa_win_percent = 100.0 * (automa_total_wins / amount)
    human_win_percent = 100.0 * (tallies["human"] / amount)
    resource_averages = [quantity / amount for quantity in metrics["end_resources"]]

    avg_consumed = {
        kind: {
            "human": metrics["consumed_resources"][kind]["human"] / amount,
            "automa": metrics["consumed_resources"][kind]["automa"] / amount,
        }
        for kind in ["coal", "oil", "trash", "nuke"]
    }

    summary_lines = [
        f"=== Power Grid Simulation Summary ({amount} Games) ===",
        f"Map: {map_data['name']} | Players: {player_count}",
        "",
        "--- Win Rates ---",
        f"Human Wins:        {human_win_percent:5.2f}% [{tallies['human']}]",
        f"Automa Total Wins: {automa_win_percent:5.2f}% [{automa_total_wins}]",
        f"  - Automa Left:   {100.0 * (tallies['automa_left'] / amount):5.2f}% [{tallies['automa_left']}]",
        f"  - Automa Right:  {100.0 * (tallies['automa_right'] / amount):5.2f}% [{tallies['automa_right']}]",
        f"City Trigger Wins: Human [{metrics['human_city_wins']}], Automa [{metrics['automa_city_wins']}]",
        f"Tiebreaker Wins:   Human [{metrics['human_tiebreaker_wins']}], Automa [{metrics['automa_tiebreaker_wins']}]",
        "",
        "--- Game Length (Turns) ---",
        f"Average: {mean(metrics['turns']):.2f}",
        f"Median:  {median(metrics['turns'])}",
        f"Min:     {min(metrics['turns'])}",
        f"Max:     {max(metrics['turns'])}",
        "",
        "--- Cities Built at End Game ---",
        f"Human:        avg={mean(metrics['human_cities']):.2f}, min={min(metrics['human_cities'])}, max={max(metrics['human_cities'])}",
        f"Automa Left:  avg={mean(metrics['left_cities']):.2f}, min={min(metrics['left_cities'])}, max={max(metrics['left_cities'])}",
        f"Automa Right: avg={mean(metrics['right_cities']):.2f}, min={min(metrics['right_cities'])}, max={max(metrics['right_cities'])}",
        "",
        "--- Human Economy ---",
        f"Ending Money:          avg=${mean(metrics['human_money']):.2f}, min=${min(metrics['human_money'])}, max=${max(metrics['human_money'])}",
        f"Ending Power Capacity: avg={mean(metrics['human_power_capacity']):.2f}, min={min(metrics['human_power_capacity'])}, max={max(metrics['human_power_capacity'])}",
        "",
        "--- Resource Market State at End Game (Average Remaining) ---",
        f"Coal:  {resource_averages[0]:.2f}",
        f"Oil:   {resource_averages[1]:.2f}",
        f"Trash: {resource_averages[2]:.2f}",
        f"Nuke:  {resource_averages[3]:.2f}",
        "",
        "--- Average Resources Consumed Per Game ---",
        f"Coal:  Human={avg_consumed['coal']['human']:.2f}, Automa={avg_consumed['coal']['automa']:.2f}",
        f"Oil:   Human={avg_consumed['oil']['human']:.2f}, Automa={avg_consumed['oil']['automa']:.2f}",
        f"Trash: Human={avg_consumed['trash']['human']:.2f}, Automa={avg_consumed['trash']['automa']:.2f}",
        f"Nuke:  Human={avg_consumed['nuke']['human']:.2f}, Automa={avg_consumed['nuke']['automa']:.2f}",
        "",
        "--- Outliers and Anomalies ---",
        f"Long Games (>= 15 turns):        count={len(metrics['outliers']['long_games'])}, IDs={metrics['outliers']['long_games'][:15]}",
        f"Short Games (<= 9 turns):       count={len(metrics['outliers']['short_games'])}, IDs={metrics['outliers']['short_games'][:15]}",
        f"Unpowered Endgame (Cap < Built): count={len(metrics['outliers']['unpowered_endgame'])}, IDs={metrics['outliers']['unpowered_endgame'][:15]}",
        f"Cash Starvation (Money <= $5):   count={len(metrics['outliers']['low_cash_human'])}, IDs={metrics['outliers']['low_cash_human'][:15]}",
        f"Tiebreaker Decided:              count={len(metrics['outliers']['tiebreakers'])}, IDs={metrics['outliers']['tiebreakers'][:15]}",
    ]

    summary_output = "\n".join(summary_lines)
    for line in summary_lines:
        debug.result(line)
    debug.save_summary(summary_output + "\n")
