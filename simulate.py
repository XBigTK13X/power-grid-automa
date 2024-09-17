import game_data

DEBUG_SIM=True

def debug_sim(message):
    if DEBUG_SIM:
        print(message)

def play_games(cards,amount):
    print(f"Simulating {amount} games of Power Grid")
    tallies = [0,0]
    results = []
    for ii in range(0,amount):
        result = play_game(cards)
        results.append(result)
        if result.human_win:
            tallies[0]+=1
        else:
            tallies[1]+=1
    percent = 100.0*(tallies[1]/(tallies[1]+tallies[0]))
    print(f"The automa won {percent}% [{tallies[1]}] games and the human won [{tallies[0]}] games")
    average_turns = sum([x.turns_taken for x in results])/len(results)
    print(f'On average, the game was over after [{average_turns}] turns')
    print(f'Win stats automa-city[{sum([x.automa_city_win for x in results])/len(results)}] human-city[{sum([x.human_city_win for x in results])/len(results)}]')
    print(f'Tiebreaker stats automa[{sum([x.automa_tiebreaker_win for x in results])/len(results)}] human[{sum([x.human_tiebreaker_win for x in results])/len(results)}]')

class GameResult:
    def __init__(self):
        self.automa_score = 0
        self.automa_tiebreaker = 0
        self.human_cities = 0
        self.human_money = 0
        self.human_plants = []
        self.human_power_capacity = 0
        self.human_score = 0
        self.human_win = False
        self.turns_taken = 0
        self.automa_city_win = False
        self.human_city_win = False
        self.automa_tiebreaker_win = False
        self.human_tiebreaker_win = False

    def calculate_winner(self):
        # TODO Actually calculate how many plants will fire, not just capacity
        if self.human_score > self.human_power_capacity:
            human_score = self.human_power_capacity
        if self.automa_score > self.human_score:
            debug_sim("Automa wins")
            self.automa_city_win = True
            return False
        if self.automa_score < self.human_score:
            debug_sim("Human wins")
            self.human_city_win = True
            return True
        if self.automa_score == self.human_score:
            if self.human_power_capacity < self.human_score:
                debug_sim("Automa wins")
                self.tiebreaker_automa_win = True
                return False
            else:
                if self.human_money <= self.automa_tiebreaker:
                    debug_sim(f"Automa wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker()}")
                    self.tiebreaker_automa_win = True
                    return False
                else:
                    debug_sim(f"Human wins with tiebreaker. Human money ${self.human_money} to {self.automa_tiebreaker}")
                    self.human_tiebreaker_win = True
                    return True

def play_game(cards):
    game_map = game_data.fresh_map()
    plant_market = game_data.fresh_market()
    automa = game_data.fresh_automa(cards)
    human = game_data.fresh_human()

    human_score = 0
    automa_score = 0
    human_player_order = 3
    end_game_score = 15
    turn_count = 0
    first_turn = True
    step = 1
    while automa_score < end_game_score and human_score < end_game_score:
        debug_sim(f"\n=-=-=-=-TURN {turn_count + 1 }-=-=-=-=")
        automa.draw_cards()
        if first_turn:
            while not automa.has_four_auction_plants():
                automa.draw_cards()
        # Phase 1 - Player Order
        if not first_turn:
            if automa_score > human_score:
                human_player_order = 5
            if human_score > automa_score:
                human_player_order = 1
            if human_score == automa_score:
                 human_player_order = automa.get_player_order(human.get_highest_plant())

        # Phase 2 - Plant Auction
        human_purchased = False
        for ii in range(1,6):
            ante = 0
            if plant_market.is_empty():
                continue
            if human_player_order != 5:
                ante = automa.get_current_ante()
            if ii == human_player_order:
                next_plant = plant_market.random()
                if not human_purchased and human.purchase_plant(plant_market,next_plant,ante,can_ignore=(not first_turn)):
                    human_purchased = True
                    debug_sim(f"Human bought plant {next_plant.cost} for ${next_plant.cost + ante}")
                    debug_sim(f"Human plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}")
                    if plant_market.refill():
                        step = 3
                else:
                    plant_market.replace(next_plant)
            else:
                if not plant_market.has_plant(automa.get_plant_auction_index()):
                    automa.next_auction_index()
                    continue
                next_plant = plant_market.take_plant(automa.get_plant_auction_index())
                if human_purchased or not human.purchase_plant(plant_market,next_plant,ante):
                    automa.claim_plant(next_plant)
                    automa.next_auction_index()
                else:
                    human_purchased = True
                if plant_market.refill():
                    step = 3
        debug_sim("Automa plants")
        debug_sim([f'#{x.cost} - {x.resource_kind} x {x.resource_amount}' for x in automa.plants])
        debug_sim("Human plants")
        debug_sim([f'#{x.cost} - {x.resource_kind} x {x.resource_amount}' for x in human.plants])

        if first_turn:
            human_player_order = automa.get_player_order(human.get_highest_plant())
            debug_sim(f"Human's first player order is {human_player_order}")

        # Phase 3 - Purchase Resources
        debug_sim("Starting resource market")
        game_map.resource_market.debug()
        for ii in range(1,6):
            action_index = 6 - ii
            if human_player_order == action_index:
                filled_orders = human.purchase_resources(game_map.resource_market)
                debug_sim(f"Human filled resource orders {filled_orders}")
            else:
                active_plant = automa.get_resource_purchase_plant()
                resource_amount = active_plant.resource_amount*automa.get_resource_purchase_mult()
                if active_plant.resource_kind != 'wind':
                    purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,automa.money)
                    debug_sim(f"Automa took {taken} {active_plant.resource_kind} from the resource market")
        debug_sim("Ending resource market")
        game_map.resource_market.debug()

        # Phase 4 - Build Houses
        for ii in range(1,6):
            action_index = 6 - ii
            if human_player_order == action_index:
                built,cost = human.build_houses(game_map,step)
                debug_sim(f'Human built {built} houses for ${cost}')
            else:
                built = automa.build_houses(game_map,step)
                debug_sim(f'Automa built {built} houses')


        automa_score += automa.get_build_score()
        human_score = human.houses
        if step == 1:
            if automa_score > 7 or human_score > 7:
                step = 2

        # Phase 5 - Bureaucracy
        automa.reset_indices()
        game_map.resource_market.refill_phase(step)
        human.power_cities()
        if step == 1 or step == 2:
            if plant_market.cycle_highest():
                step = 3
        if step == 3:
            plant_market.remove_lowest()
        first_turn = False
        turn_count += 1
        debug_sim(f"Finished turn {turn_count} on step {step}")
        debug_sim(f"automa score {automa_score}")
        debug_sim(f"human score {human_score}")
        human.debug()
    automa.debug()
    human.debug()
    debug_sim(f"Automa score {automa_score}")
    debug_sim(f"Human score {human_score} cities and power {human.power_capacity()}")
    result = GameResult()
    result.human_score = human_score
    result.automa_score = automa_score
    result.turns_taken = turn_count
    result.human_money = human.money
    result.human_power_capacity = human.power_capacity()
    result.automa_tiebreaker = automa.tiebreaker()
    result.human_plants = [x.cost for x in human.plants]
    result.automa_plants = [x.cost for x in automa.plants]
    result.human_win = result.calculate_winner()
    debug_sim(f"The game took {turn_count} turns")
    return result




