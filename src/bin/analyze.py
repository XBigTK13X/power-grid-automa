import src.board as board
import src.automa_card_info as automa_card_info
import src.generate as generate
import src.model as model

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

    import pprint
    pprint.pprint({
        'map': map['name'],
        'cities': city_count,
        'per_region': cities_per_region,
        'player_count_report': player_details
    })

def count_turns(deck):
    deck.pop()
    deck.pop()
    deck.pop()
    end_game_score = 17
    card_index = 0
    current_score = 0
    turns = 0
    build_count = 0
    while current_score < end_game_score:
        card = deck[card_index % len(deck)]
        current_score += card.score
        build_count += card.build_count
        card_index += 1
        turns += 1
    return turns,build_count

def analyze_automa():
    cards = [model.AutomaCard(xx) for xx in generate.create_cards()]
    low_score_turns,low_score_build_count = count_turns(sorted(cards,key=lambda xx:xx.score))
    high_score_turns,high_score_build_count = count_turns(sorted(cards,key=lambda xx:xx.score,reverse=True))
    low_build_turns,low_build_build_count = count_turns(sorted(cards,key=lambda xx:xx.build_count))
    high_build_turns,high_build_build_count = count_turns(sorted(cards,key=lambda xx:xx.build_count,reverse=True))

    print("Market distribution")
    hits = {}
    for market in automa_card_info.manual_plant_choices:
        for hit in market:
            if not hit in hits:
                hits[hit] = 0
            hits[hit] += 1

    import pprint
    pprint.pprint(hits,width=2)

    print("Build distribution")
    hits = {}
    for manual_build in automa_card_info.manual_builds:
        for hit in manual_build:
            if not hit in hits:
                hits[hit] = 0
            hits[hit] += 1
    import pprint
    pprint.pprint(hits,width=2)
    print(f"The game ends when someone scores 17 points")
    print(f"The longest the automa will take is {low_score_turns} turns")
    print(f"The shortest the automa will take is {high_score_turns} turns")
    print(f"The automa will place at minimum {low_build_build_count} buildings")
    print(f"The automa will place at maximum {high_build_build_count} buildings")

analyze_board(board.united_states_of_america)
analyze_board(board.germany)
analyze_automa()