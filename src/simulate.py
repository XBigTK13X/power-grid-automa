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
    automa = model.Automa(player_count,cards)
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
    human_player_order = 3
    automa_1_player_order = 1
    automa_2_player_order = 2
    automa_1_cities_built = 0
    automa_2_cities_built = 0
    human_cities_built = 0
    debug.sim("Entering sim loop")
    player_order_sort = [{'name':'player','score':0,'plant':0},{'name':'automa_1','score':0,'plant':0},{'name':'automa_2','score':0,'plant':0}]
    while automa_1_cities_built < game_map.end_game_city_count \
        and automa_2_cities_built < game_map.end_game_city_count \
        and human_cities_built < game_map.end_game_city_count:
        debug.sim(f"\n\n\n=-=-=-=-TURN {turn_count + 1 }-=-=-=-=")

        automa.draw_cards()
        if first_turn:
            while not automa.has_four_auction_plants():
                automa.draw_cards()

        debug.sim("Determining player order")
        # Phase 1 - Player Order
        if not first_turn:
            for ii in range(0,len(player_order_sort)):
                entry = player_order_sort[ii]
                #if entry.name == 'player'
            #if human_cities_built
            if automa_score > human_score:
                human_player_order = player_count
            if human_score > automa_score:
                human_player_order = 1
            if human_score == automa_score:
                 human_player_order = automa.get_player_order(human.get_highest_plant())
        debug.sim(f"Human is player {human_player_order} with ${human.money}")

        # Phase 2 - Plant Auction
        human_purchased = False
        debug.sim("Purchasing plants")
        for ii in range(1,player_count+1):
            ante = 0
            if plant_market.is_empty():
                continue
            if human_player_order != player_count:
                ante = automa.get_current_ante()
            if ii == human_player_order:
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
                if not plant_market.has_plant(automa.get_plant_auction_index()):
                    automa.next_auction_index()
                    continue
                next_plant = plant_market.take_plant(automa.get_plant_auction_index())
                if human_purchased or not human.purchase_plant(plant_market,next_plant,ante):
                    debug.sim(f"Automa purchased plant {next_plant.cost}")
                    automa.claim_plant(next_plant)
                    automa.next_auction_index()
                else:
                    debug.sim(f"Human purchased plant powers {next_plant.power_output} city for {next_plant.resource_amount} {next_plant.resource_kind}")
                    human_purchased = True
                if plant_market.refill():
                    step = 3

        if first_turn:
            human_player_order = automa.get_player_order(human.get_highest_plant())
            debug.sim(f"Human's first player order is {human_player_order}")

        # Phase 3 - Purchase Resources
        debug.sim("Starting resource market")
        game_map.resource_market.debug()
        for ii in range(1,player_count+1):
            action_index = player_count + 1 - ii
            if human_player_order == action_index:
                filled_orders = human.purchase_resources(game_map.resource_market)
                for filled_order in filled_orders:
                    resource_purchase_tracker[filled_order[0]]['human'] += filled_order[1]
                debug.sim(f"Human filled resource orders {filled_orders}")
            else:
                for active_plant in automa.get_resource_purchase_plants(action_index):
                    resource_amount = active_plant.resource_amount*automa.get_resource_purchase_mult()
                    if active_plant.resource_kind != 'wind':
                        if active_plant.resource_kind == 'oil/coal':
                            start_amounts = game_map.resource_market.amounts()
                            purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,automa.money)
                            debug.sim(f"Automa took {taken} {active_plant.resource_kind} from the resource market")
                            end_amounts = game_map.resource_market.amounts()
                            if end_amounts[0] != start_amounts[0]:
                                resource_purchase_tracker['coal']['automa'] += start_amounts[0] - end_amounts[0]
                            if end_amounts[1] != start_amounts[1]:
                                resource_purchase_tracker['oil']['automa'] += start_amounts[1] - end_amounts[1]
                        else:
                            purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,automa.money)
                            resource_purchase_tracker[active_plant.resource_kind]['automa'] += taken
                            debug.sim(f"Automa took {taken} {active_plant.resource_kind} from the resource market")
        debug.sim("Ending resource market")
        game_map.resource_market.debug()

        # Phase 4 - Build Houses
        debug.sim("Starting city building")
        for ii in range(1,player_count+1):
            action_index = player_count + 1 - ii
            if human_player_order == action_index:
                built,cost = human.build_houses(game_map,step)
                if built == None:
                    debug.sim("Human unable to find a free space!")
                else:
                    human_cities_built += built
                    debug.sim(f'Human built {built} houses for ${cost}')
            else:
                built = automa.build_houses(game_map,step)
                if built == None:
                    debug.sim("Automa unable to find a free space!")
                else:
                    automa_cities_built += built
                    debug.sim(f'Automa built {built} houses')


        automa_score += automa.get_build_score()
        human_score = human.houses
        if step == 1:
            if automa_score > game_map.step_2_city_count or human_score > game_map.step_2_city_count:
                step = 2

        # Phase 5 - Bureaucracy
        automa.reset_indices()
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
        debug.sim(f"automa score {automa_score}")
        debug.sim(f"human score {human_score}")
        automa.debug()
        human.debug()
        game_map.debug()

    debug.sim(f"Automa score {automa_score}")
    debug.sim(f"Human score {human_score} cities and power {human.power_capacity()}")
    #import pprint
    #pprint.pprint(resource_purchase_tracker)
    debug.sim(f'Automa built in {automa_cities_built} cities and human built in {human_cities_built} cities')
    result = model.GameResult()
    result.human_score = human_score
    result.automa_score = automa_score
    result.turns_taken = turn_count
    result.human_money = human.money
    result.human_power_capacity = human.power_capacity()
    result.automa_tiebreaker = automa.tiebreaker()
    result.human_plants = [x.cost for x in human.plants]
    result.automa_plants = []
    for ii in range(0,len(automa.plant_stacks)):
     result.automa_plants.append([x.cost for x in automa.plant_stacks[ii]])
    result.human_win = result.calculate_winner()
    debug.sim(f"The game took {turn_count} turns")
    return result




