import src.debug as debug

import csv
import random

import src.automa_card_info as automa_card_info

def create_cards():
    debug.sim("==Automa deck stats==")
    manual_build_card_totals = [sum(x) for x in automa_card_info.manual_builds]
    debug.sim("card build totals")
    debug.sim(manual_build_card_totals)
    debug.sim("Low build total")
    manual_build_card_totals.sort()
    debug.sim(sum(manual_build_card_totals[0:8]))
    debug.sim("High build total")
    manual_build_card_totals.reverse()
    debug.sim(sum(manual_build_card_totals[0:8]))
    debug.sim("Score amounts")
    scores = []
    for xx in automa_card_info.manual_builds:
        scores.append(len([yy for yy in xx if yy > 1]))
    debug.sim(scores)

    random.shuffle(automa_card_info.ante)
    random.shuffle(automa_card_info.compass)
    random.shuffle(automa_card_info.resource)
    random.shuffle(automa_card_info.builders)
    random.shuffle(automa_card_info.mults)

    random.shuffle(automa_card_info.manual_scores)
    random.shuffle(automa_card_info.manual_plant_choices)
    random.shuffle(automa_card_info.manual_builds)
    random.shuffle(automa_card_info.manual_resources)

    deck_count = 24
    cards = []
    for ii in range(0,deck_count):
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
        card['mult'] = f'x{automa_card_info.mults[ii % len(automa_card_info.mults)]}'
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
        card['refill_delta'] = -1 * automa_card_info.resource[ii % len(automa_card_info.resource)]
        resources = automa_card_info.manual_resources[ii % len(automa_card_info.manual_resources)]
        card['resource1'] = f'{resources[0]}x'
        card['resource2'] = f'{resources[1]}x'
        compass = automa_card_info.compass_lookup[automa_card_info.compass[ii % len(automa_card_info.compass)]]
        card['compass_rotation'] = compass[0]
        card['compass_direction'] = compass[1]
        card['compass_display'] = f'{compass[1]}'
        build = automa_card_info.manual_builds[ii % len(automa_card_info.manual_builds)]
        card['build1'] = build[0]
        card['build2'] = build[1]
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
        'mult',
        'refill_delta',
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