import src.board as board
import src.automa_card_info as automa_card_info

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

def analyze_automa():
    # TODO This isn't working since the refactor, finite loops in the low count
    city_max = 14
    low_city = 0
    low_turn = 0
    low_index = 0
    def calc_build(amounts):
        return len([x for x in amounts if x > 1])

    manual_build_totals = [calc_build(x) for x in automa_card_info.manual_builds]
    manual_build_totals.sort()
    low_circuit = 100
    while low_city < city_max:
        low_circuit -= 1
        if low_circuit <= 0:
            print("Unable to calculate low city")
            break;
        if low_index > 8:
            low_index = 0
        low_city += manual_build_totals[low_index]
        low_index += 1
        low_turn += 1
        print(manual_build_totals[low_index])

    city_max = 14
    high_city = 0
    high_turn = 0
    high_index = 23
    high_circuit = 100
    while high_city < city_max:
        high_circuit -= 1
        if high_circuit <= 0:
            print("Unable to calculate high city")
            break;
        if high_index < 15:
            high_index = 23
        high_city += manual_build_totals[high_index]
        high_index -= 1
        high_turn += 1
        print('high')

    hits = [0,0,0,0,0]
    for market in automa_card_info.manual_markets:
        for hit in market:
            hits[hit] += 1

    print("Market distribution")
    print(hits)

    hits = [0,0,0,0,0]
    for res in automa_card_info.manual_resources:
        for hit in res:
            hits[hit] += 1
    print("Resource distribution")
    print(hits)

    hits = [0,0,0,0,0]
    for manual_build in automa_card_info.manual_builds:
        for hit in manual_build:
            hits[hit] += 1
    print("build distribution")
    print(hits)
    print(f"The longest the automa will take is {low_turn} turns")
    print(f"The shortest the automa will take is {high_turn} turns")

analyze_board(board.united_states_of_america)
analyze_board(board.germany)
analyze_automa