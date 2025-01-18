import src.debug as debug

import csv
import random

import src.automa_card_info as automa_card_info
import src.model as model

def create_cards():
    debug.sim("==Building automa cards==")

    cards_in_deck = 24
    cards = []
    for ii in range(0,cards_in_deck):
        card = {}
        market = list(automa_card_info.manual_plant_choices[ii % len(automa_card_info.manual_plant_choices)])
        card['market1'] = market[0]
        card['market2'] = market[1]
        ante = automa_card_info.manual_antes[ii % len(automa_card_info.manual_antes)]
        card['ante1'] = ante[0]
        card['ante2'] = ante[1]
        card['compass_index_1'] = automa_card_info.compass[ii % len(automa_card_info.compass)]
        card['compass_direction_1'] = model.get_compass(card['compass_index_1'])[1]
        card['compass_index_2'] = automa_card_info.compass[(ii + 4) % len(automa_card_info.compass)]
        card['compass_direction_2'] = model.get_compass(card['compass_index_2'])[1]
        build = automa_card_info.manual_builds[ii % len(automa_card_info.manual_builds)]
        card['build1'] = build[0]
        card['build2'] = build[1]
        resources = automa_card_info.manual_resources[ii % len(automa_card_info.manual_resources)]
        card['resource1'] = resources[0]
        card['resource2'] = resources[1]
        card['id'] = f'F{ii+1:02}'
        cards.append(card)
    return cards

def write_cards_to_csv(cards):
    headers = [
        'id',
        'market1',
        'market2',
        'ante1',
        'ante2',
        'resource1',
        'resource2',
        'compass_index_1',
        'compass_direction_1',
        'compass_index_2',
        'compass_direction_2',
        'build1',
        'build2'
    ]
    with open('./card/powergrid.csv','w', newline='') as write_handle:
        writer = csv.DictWriter(write_handle,headers)
        writer.writeheader()
        writer.writerows(cards)