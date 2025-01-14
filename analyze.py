import game_map

def analyze(map):
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
analyze(game_map.united_states_of_america)
analyze(game_map.germany)