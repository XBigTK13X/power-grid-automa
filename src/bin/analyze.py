import src.board as board
import src.automa_card_info as automa_card_info
import src.generate as generate
import src.model as model
import pprint

def analyze_board(map):
    city_count = len(map['cities'])
    cities_per_region = [0,0,0,0,0,0]
    for region in range(1,7):
        for city in map['cities']:
            if city[0] == region:
                cities_per_region[region-1] += 1
    cities_per_step_max = [0,0,0,0,0]
    cities_per_step_min = [0,0,0,0,0]
    player_details = [{},{},{},{},{}]
    for player_count in range(0,5):
        info = map['player_count_info'][player_count]
        regions_used = info[0]
        cities_per_region.sort()
        cities_per_step_min[player_count] = 0
        cities_per_step_max[player_count] = 0
        for ii in range(0,regions_used):
            cities_per_step_min[player_count] += cities_per_region[ii]
            cities_per_step_max[player_count] += cities_per_region[5-ii]
        player_details[player_count] = {
            'player_count': player_count + 2,
            'max_cities': cities_per_step_max[player_count],
            'min_cities': cities_per_step_min[player_count],
            'regions_used': regions_used,
            'plants_removed': info[1],
            'plants_per_player': info[2],
            'step_2_city_count': info[3],
            'end_game_city_count': info[4]
        }
    pprint.pprint({
        'map': map['name'],
        'cities': city_count,
        'per_region': cities_per_region,
        'player_count_report': player_details
    })

def count_turns(build_index,deck):
    deck.pop()
    deck.pop()
    deck.pop()
    end_game_score = 17
    card_index = 0
    current_score = 0
    turns = 0
    while current_score < end_game_score:
        card = deck[card_index % len(deck)]
        current_score += card.left_half.build_amount if build_index == 0 else card.right_half.build_amount
        card_index += 1
        turns += 1
    return turns,current_score

def analyze_automa():
    cards = [model.AutomaCard(xx) for xx in generate.create_cards()]
    low_build_1_turns,low_build_1_count = count_turns(0,sorted(cards,key=lambda xx:xx.left_half.build_amount))
    high_build_1_turns,high_build_1_count = count_turns(0,sorted(cards,key=lambda xx:xx.left_half.build_amount,reverse=True))
    low_build_2_turns,low_build_2_count = count_turns(1,sorted(cards,key=lambda xx:xx.right_half.build_amount))
    high_build_2_turns,high_build_2_count = count_turns(1,sorted(cards,key=lambda xx:xx.right_half.build_amount,reverse=True))

    print("Plant market pick distribution")
    hits = {'left':{},'right':{}}
    for market in automa_card_info.manual_plant_choices:
        left_hit = market[0]
        if not left_hit in hits['left']:
            hits['left'][left_hit] = 0
        hits['left'][left_hit] += 1

        right_hit = market[1]
        if not right_hit in hits['right']:
            hits['right'][right_hit] = 0
        hits['right'][right_hit] += 1
    pprint.pprint(hits,indent=2,width=2)

    print("Ante distribution")
    hits = {'left':{},'right':{}}
    for ante in automa_card_info.manual_antes:
        left_hit = ante[0]
        if not left_hit in hits['left']:
            hits['left'][left_hit] = 0
        hits['left'][left_hit] += 1

        right_hit = ante[1]
        if not right_hit in hits['right']:
            hits['right'][right_hit] = 0
        hits['right'][right_hit] += 1
    pprint.pprint(hits,indent=2,width=2)

    print("Resource mult distribution")
    hits = {'left':{},'right':{}}
    for resource in automa_card_info.manual_resources:
        left_hit = resource[0]
        if not left_hit in hits['left']:
            hits['left'][left_hit] = 0
        hits['left'][left_hit] += 1

        right_hit = resource[1]
        if not right_hit in hits['right']:
            hits['right'][right_hit] = 0
        hits['right'][right_hit] += 1
    pprint.pprint(hits,indent=2,width=2)

    print(f"The game ends when someone scores 17 points")
    print(f"Automa 1 will take at least {high_build_1_turns} turns and at most {low_build_1_turns}")
    print(f"Automa 2 will take at least {high_build_2_turns} turns and at most {low_build_2_turns}")

#analyze_board(board.united_states_of_america)
#analyze_board(board.germany)
analyze_automa()