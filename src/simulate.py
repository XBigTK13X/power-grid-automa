import src.debug as debug
import src.model as model

def play_games(cards, amount, map, player_count):
    print(f"Simulating {amount} games of Power Grid")
    tallies = [0,0]
    results = []
    for ii in range(0,amount):
        if(ii % 100 == 0):
            print(f"Simulating game {ii+1}/{amount}")
        result = play_game(cards,map,player_count)
        results.append(result)
        if result.human_win:
            tallies[0]+=1
        else:
            tallies[1]+=1
    percent = 100.0*(tallies[1]/(tallies[1]+tallies[0]))
    debug.result(f"The automa won {percent:02}% [{tallies[1]}] games and the human won {100-percent:02}% [{tallies[0]}] games")
    average_turns = sum([x.turns_taken for x in results])/len(results)
    min_turns = min([x.turns_taken for x in results])
    max_turns = max([x.turns_taken for x in results])
    debug.result(f'On average, the game was over after [{average_turns}] turns. Shortest was {min_turns} turns. Longest was {max_turns} turns')
    debug.result(f'Win stats automa-city[{sum([x.automa_city_win for x in results])/len(results)}] human-city[{sum([x.human_city_win for x in results])/len(results)}]')
    debug.result(f'Tiebreaker stats automa[{sum([x.automa_tiebreaker_win for x in results])/len(results)}] human[{sum([x.human_tiebreaker_win for x in results])/len(results)}]')
    debug.result(f'Human money at end game averaged [{sum([x.human_money for x in results])/len(results)}] with a min [{min([x.human_money for x in results])}] and max [{max([x.human_money for x in results])}]')

def play_game(cards,map,player_count):
    debug.sim("Setting up a new game")
    game_map = model.GameMap(map,player_count)
    plant_market = model.PlantMarket(model.original_plants)
    automa = model.Automa(cards)
    human = model.Human()

    turn_count = 0
    first_turn = True
    step = 1
    start_resource_amounts = game_map.resource_market.amounts()
    resource_purchase_tracker = {
        'oil':{'human':0,'automa':0,'refill':start_resource_amounts[0]},
        'coal':{'human':0,'automa':0,'refill':start_resource_amounts[1]},
        'trash':{'human':0,'automa':0,'refill':start_resource_amounts[2]},
        'nuke':{'human':0,'automa':0,'refill':start_resource_amounts[3]}
    }
    automa_left_player_order = 0
    automa_right_player_order = 2
    human_player_order = 1

    automa_left_cities_built = 0
    automa_right_cities_built = 0
    human_cities_built = 0
    debug.sim("Entering sim loop")
    while automa_left_cities_built < game_map.end_game_city_count \
        and automa_right_cities_built < game_map.end_game_city_count \
        and human_cities_built < game_map.end_game_city_count:
        debug.sim(f"\n\n\n=-=-=-=-TURN {turn_count + 1 }-=-=-=-=")
        if turn_count > 20:
            print("An error occurred during simulation.")
            print("The game will never take more than 20 turns")
            return None

        automa.draw_cards()
        if first_turn:
            # Both automa players MUST claim a plant during the first turn of the game
            while automa.has_market_skips():
                automa.draw_cards()

        debug.sim("\n - Phase 1 - Player Order")
        # Phase 1 - Player Order
        if not first_turn:
            player_order_sort = sorted([
                {'name':'human','score':human_cities_built,'plant':human.plants[0].cost},
                {'name':'automa_left','score':automa_left_cities_built,'plant':automa.left_player.plant_stack[0].cost},
                {'name':'automa_right','score':automa_right_cities_built,'plant':automa.right_player.plant_stack[0].cost}
            ],key=lambda xx:(xx['score'],xx['plant']))
            for ii in range(0,len(player_order_sort)):
                player_order = player_order_sort[ii]
                if player_order['name'] == 'human':
                    human_player_order = ii
                elif player_order['name'] == 'automa_left':
                    automa_left_player_order = ii
                elif player_order['name'] == 'automa_right':
                    automa_right_player_order = ii
        debug.sim(f"Human is player {human_player_order} starting with ${human.money}")
        debug.sim(f"AutomaLeft is player {automa_left_player_order} ")
        debug.sim(f"AutomaRight is player {automa_right_player_order}")

        # Phase 2 - Plant Auction
        human_purchased = False
        debug.sim("\n - Phase 2 - Power Plant Auction")
        has_bought = []
        for action_index in range(0,player_count):
            if plant_market.is_empty():
                continue
            ante = automa.get_current_ante(has_bought)

            if action_index == human_player_order:
                next_plant = plant_market.random()
                if not human_purchased and human.purchase_plant(plant_market,next_plant,ante,can_ignore=(not first_turn)):
                    human_purchased = True
                    debug.sim(f"Human bought plant {next_plant.cost} for ${next_plant.cost + ante}")
                    debug.sim(f"Human plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}")
                    if plant_market.refill():
                        step = 3
                else:
                    debug.sim("The human did not purchase a plant")
                    plant_market.replace(next_plant)
            else:
                automa_side = model.LEFT_SIDE if action_index == automa_left_player_order else model.RIGHT_SIDE
                automa_name = 'AutomaLeft' if automa_side == model.LEFT_SIDE else 'AutomaRight'
                has_bought.append(automa_side)
                if not plant_market.has_plant(automa.get_plant_auction_index(automa_side)):
                    continue
                next_plant = plant_market.take_plant(automa.get_plant_auction_index(automa_side))
                if human_purchased or not human.purchase_plant(plant_market,next_plant,ante):
                    debug.sim(f"{automa_name} purchased plant {next_plant.cost}")
                    debug.sim(f"{automa_name} plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}")
                    automa.claim_plant(next_plant,automa_side)
                else:
                    debug.sim(f"Human purchased plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}")
                    human_purchased = True
                if plant_market.refill():
                    step = 3

        if first_turn:
            player_order_sort = sorted([
                {'name':'human','score':human_cities_built,'plant':human.plants[0].cost},
                {'name':'automa_left','score':automa_left_cities_built,'plant':automa.left_player.plant_stack[0].cost},
                {'name':'automa_right','score':automa_right_cities_built,'plant':automa.right_player.plant_stack[0].cost}
            ],key=lambda xx:(xx['score'],xx['plant']))
            for ii in range(0,len(player_order_sort)):
                player_order = player_order_sort[ii]
                if player_order['name'] == 'human':
                    human_player_order = ii
                elif player_order['name'] == 'automa_left':
                    automa_left_player_order = ii
                elif player_order['name'] == 'automa_right':
                    automa_right_player_order = ii
            debug.sim(f"Human's first turn player order is {human_player_order}")

        # Phase 3 - Purchase Resources
        debug.sim("\n - Phase 3 - Purchase Resources")
        game_map.resource_market.debug()
        for ii in range(0, player_count):
            action_index = player_count - ii - 1
            if human_player_order == action_index:
                filled_orders = human.purchase_resources(game_map.resource_market)
                for filled_order in filled_orders:
                    resource_purchase_tracker[filled_order[0]]['human'] += filled_order[1]
                debug.sim(f"Human filled resource orders {filled_orders}")
            else:
                automa_side = model.LEFT_SIDE if action_index == automa_left_player_order else model.RIGHT_SIDE
                automa_name = 'AutomaLeft' if automa_side == model.LEFT_SIDE else 'AutomaRight'
                is_first = True
                for active_plant in automa.get_resource_purchase_plants(automa_side):
                    resource_amount = active_plant.resource_amount
                    if is_first:
                        resource_amount *= 2
                        is_first = False
                    if active_plant.resource_kind != 'wind':
                        if active_plant.resource_kind == 'oil/coal':
                            start_amounts = game_map.resource_market.amounts()
                            purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,10000)
                            debug.sim(f"{automa_name} took {taken} {active_plant.resource_kind} from the resource market")
                            end_amounts = game_map.resource_market.amounts()
                            if end_amounts[0] != start_amounts[0]:
                                resource_purchase_tracker['coal']['automa'] += start_amounts[0] - end_amounts[0]
                            if end_amounts[1] != start_amounts[1]:
                                resource_purchase_tracker['oil']['automa'] += start_amounts[1] - end_amounts[1]
                        else:
                            purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,10000)
                            resource_purchase_tracker[active_plant.resource_kind]['automa'] += taken
                            debug.sim(f"{automa_name} took {taken} {active_plant.resource_kind} from the resource market")
        debug.sim("Ending resource market")
        game_map.resource_market.debug()

        # Phase 4 - Build Houses
        debug.sim("\n - Phase 4 - Build Cities")
        for ii in range(0,player_count):
            action_index = player_count - ii - 1
            if human_player_order == action_index:
                built,cost = human.build_houses(game_map,step)
                if built == None:
                    debug.sim("Human unable to find a free space!")
                else:
                    human_cities_built += built
                    debug.sim(f'Human built {built} houses for ${cost}')
            else:
                automa_side = model.LEFT_SIDE if action_index == automa_left_player_order else model.RIGHT_SIDE
                automa_name = 'AutomaLeft' if automa_side == model.LEFT_SIDE else 'AutomaRight'
                built = automa.build_houses(game_map,step,automa_side)
                if built == None:
                    debug.sim(f"{automa_name} unable to find a free space!")
                else:
                    if automa_side == model.LEFT_SIDE:
                        automa_left_cities_built += built
                    else:
                        automa_right_cities_built += built
                    debug.sim(f'{automa_name} built {built} houses')


        automa_left_cities_built = automa.left_player.houses
        automa_right_cities_built = automa.right_player.houses
        human_score = human.houses
        if step == 1:
            if automa_left_cities_built > game_map.step_2_city_count \
                or automa_right_cities_built > game_map.step_2_city_count \
                or human_score > game_map.step_2_city_count:
                step = 2

        # Phase 5 - Bureaucracy
        debug.sim('\n - Phase 5 - Bureaucracy')
        refill_amounts = game_map.resource_market.refill_phase(step)
        for kind,amount in refill_amounts.items():
            resource_purchase_tracker[kind]['refill'] += amount
        human.power_cities()
        if step == 1 or step == 2:
            if plant_market.cycle_highest():
                step = 3
        if step == 3:
            plant_market.remove_lowest()
        first_turn = False
        turn_count += 1
        debug.sim(f"Finished turn {turn_count} on step {step}")
        debug.sim(f"automa left score {automa_left_cities_built}")
        debug.sim(f"automa right score {automa_right_cities_built}")
        debug.sim(f"human score {human_score}")
        automa.debug()
        human.debug()
        game_map.debug()

    debug.sim(f"Automa left score {automa_left_cities_built}")
    debug.sim(f"Automa right score {automa_right_cities_built}")
    debug.sim(f"Human score {human_score} cities and power {human.power_capacity()}")
    #import pprint
    #pprint.pprint(resource_purchase_tracker)
    debug.sim(f'Left automa built {automa_left_cities_built} , right automa built {automa_right_cities_built}, and human built {human_cities_built}')
    result = model.GameResult()
    result.human_score = human_score
    result.automa_left_cities_built = automa_left_cities_built
    result.automa_right_score = automa_right_cities_built
    result.turns_taken = turn_count
    result.human_money = human.money
    result.human_power_capacity = human.power_capacity()
    result.automa_tiebreaker = automa.tiebreaker()
    result.human_plants = [x.cost for x in human.plants]
    result.left_plants = []
    result.left_plants.append([x.cost for x in automa.left_player.plant_stack])
    result.right_plants = []
    result.right_plants.append([x.cost for x in automa.right_player.plant_stack])
    result.human_win = result.calculate_winner()
    debug.sim(f"The game took {turn_count} turns")
    return result




