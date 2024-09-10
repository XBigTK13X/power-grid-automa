import game_data

def play_games(cards,amount):
    print(f"Simulating {amount} games of Power Grid")
    for ii in range(0,amount):
        play_game(cards)

def play_game(cards):
    game_map = game_data.fresh_map()
    plant_market = game_data.fresh_market()
    automa = game_data.fresh_automa(cards)
    human = game_data.fresh_human()

    human_score = 0
    automa_score = 0
    human_player_order = 3
    active_player = 1
    end_game_score = 15
    turn_count = 0
    first_turn = True
    step = 1
    while automa_score < end_game_score and human_score < end_game_score:
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

        if first_turn:
            human_player_order = automa.get_player_order(human.get_highest_plant())

        # Phase 3 - Purchase Resources
        for ii in range(1,5):
            action_index = 6 - ii
            if human_player_order == action_index:
                human.purchase_resources(game_map.resource_market)
            else:
                active_plant = automa.get_resource_purchase_plant()
                resource_amount = active_plant.resource_amount*automa.get_resource_purchase_mult()
                if active_plant.resource_kind != 'wind':
                    purchased,money,taken = game_map.resource_market.purchase(active_plant.resource_kind,resource_amount,automa.money)

        # Phase 4 - Build Houses
        for ii in range(1,5):
            action_index = 6 - ii
            if human_player_order == action_index:
                human.build_houses(game_map,step)
            else:
                automa.build_houses(game_map,step)

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
        print(f"Finished turn {turn_count} on step {step}")
        print(f"automa score {automa_score}")
        print(f"human score {human_score}")
    automa.debug()
    human.debug()
    print(f"Automa score {automa_score}")
    print(f"Human score {human_score}")
    print(f"The game took {turn_count} turns")


