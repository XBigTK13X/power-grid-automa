import src.debug as debug

import csv
import random

import src.automa_card_info as automa_card_info
import src.model as model

def create_cards():
    debug.sim("==Building automa cards==")

    random.shuffle(automa_card_info.ante)
    random.shuffle(automa_card_info.compass)

    cards_in_deck = 24
    cards = []
    for ii in range(0,cards_in_deck):
        card = {}
        market = list(automa_card_info.manual_plant_choices[ii % len(automa_card_info.manual_plant_choices)])
        card['market1'] = market[0]
        card['market2'] = market[1]

        passer = None if not -1 in market else market.index(-1) + 1
        base_ante = automa_card_info.ante[ii % len(automa_card_info.ante)]
        ante_delta = 1
        if base_ante > 5:
            ante_delta = 3
        if base_ante == 20:
            ante_delta = 4
        antes = []
        for jj in range(0,len(market)):
            next_ante = base_ante - (ante_delta * jj)
            if next_ante < 0:
                next_ante = 0
            antes.append(next_ante)
        antes.reverse()
        card['ante1'] = antes[0]
        card['ante2'] = antes[1]
        if passer:
            if passer == 1 or passer == 2:
                card['ante1'] = antes[1]
                card['ante2'] = 0
            if passer == 3 or passer == 4:
                card['ante1'] = 0
                card['ante2'] = antes[1]
        card['compass_index'] = automa_card_info.compass[ii % len(automa_card_info.compass)]
        compass = model.get_compass(automa_card_info.compass[ii % len(automa_card_info.compass)])
        card['compass_rotation'] = compass[0]
        card['compass_direction'] = compass[1]
        card['compass_display'] = f'{compass[1]}'
        build = automa_card_info.manual_builds[ii % len(automa_card_info.manual_builds)]
        card['build1'] = build[0]
        card['build2'] = build[1]
        resources = automa_card_info.manual_resources[ii % len(automa_card_info.manual_resources)]
        card['resource1'] = resources[0]
        card['resource2'] = resources[1]
        card['score'] = automa_card_info.manual_scores[ii % len(automa_card_info.manual_scores)]
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
        'compass_index',
        'compass_direction',
        'compass_display',
        'compass_rotation',
        'score',
        'build1',
        'build2'
    ]
    with open('./card/powergrid.csv','w', newline='') as write_handle:
        writer = csv.DictWriter(write_handle,headers)
        writer.writeheader()
        writer.writerows(cards)