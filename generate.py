import csv
import itertools
import random
import simulate

GAMES_TO_SIMULATE = 1

builds = [0,0,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2]
market_slots = [1,2,3,4]
compass = [1,2,3,4,5,6,7,8]
ante = [3,3,3,7,7,7,7,10,10,10,10,10,10,10,14,14,14,14,14,14,18,18,18,20]
resource = [2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4]
mults = [1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2]
builders = [1,2,3,4]
passers = [1,2,3,4]
market_dupes = [1,2,3]
manual_markets = [
    [1,2,3,4],
    [4,3,2,1],
    [1,1,2,3],
    [3,2,2,1],
    [1,2,3,3],
    [4,4,3,2],
    [1,4,2,3],
    [3,1,2,4],
    [2,3,4,1],
    [3,4,2,1],
    [1,2,3,-1],
    [3,2,-1,1],
    [-1,2,4,1],
    [3,-1,2,4],
    [-1,2,3,4],
    [1,-1,3,4],
    [4,1,-1,2],
    [4,1,3,-1],
    [3,2,3,4],
    [4,1,2,1],
    [2,3,1,2],
    [4,3,2,3],
    [4,1,3,4],
    [3,2,1,1],
]
manual_builds = [
    [1,0,3,1],
    [1,1,0,2],
    [1,1,1,3],
    [1,2,1,3],
    [1,1,2,3],
    [1,1,3,1],
    [1,1,3,2],
    [1,2,3,0],
    [1,2,3,1],
    [1,2,3,1],
    [1,3,1,1],
    [1,3,1,2],
    [1,3,1,2],
    [1,3,1,2],
    [1,3,2,1],
    [2,1,1,1],
    [2,1,2,1],
    [2,1,3,1],
    [2,1,3,1],
    [2,3,1,1],
    [2,3,1,1],
    [2,4,0,1],
    [3,1,1,3],
    [4,1,1,1]
]
house_total = sum([sum(x) for x in manual_builds])
print(f'The automa can build [{house_total/3}] houses with the deck')
manual_resources = [
    [0,1,0,1],
    [1,0,1,0],
    [1,0,0,1],
    [1,2,2,1],
    [1,1,1,1],
    [2,1,2,1],
    [1,2,1,2],
    [0,1,1,0],
    [1,1,3,1],
    [1,2,2,2],
    [2,2,2,1],
    [2,1,2,1],
    [1,2,1,2],
    [2,2,0,2],
    [2,0,2,2],
    [2,2,2,0],
    [0,2,2,2],
    [1,2,1,2],
    [2,1,2,1],
    [2,3,2,2],
    [2,2,3,2],
    [2,2,2,3],
    [3,2,2,2],
    [2,3,3,2],
    [3,2,2,3],
    [3,2,3,2]
]
compass_lookup = {
    1: [0,'N'],
    2: [45,'NE'],
    3: [90,'E'],
    4: [135,'SE'],
    5: [180,'S'],
    6: [225,'SW'],
    7: [270,'W'],
    8: [315,'NW']
}

market_perms = list(itertools.permutations(market_slots,4))
low_market_perms = list(itertools.permutations(market_slots,3))
random.shuffle(market_perms)
random.shuffle(low_market_perms)
random.shuffle(ante)
random.shuffle(compass)
random.shuffle(builds)
random.shuffle(resource)
random.shuffle(builders)
random.shuffle(mults)
random.shuffle(passers)
random.shuffle(market_dupes)

random.shuffle(manual_markets)
random.shuffle(manual_builds)
random.shuffle(manual_resources)

deck_count = 24
cards = []
build_one_index = 0
for ii in range(0,deck_count):
    card = {}
    market = list(manual_markets[ii % len(manual_markets)])
    card['market1'] = market[0]
    card['market2'] = market[1]
    card['market3'] = market[2]
    card['market4'] = market[3]

    passer = None if not -1 in market else market.index(-1) + 1
    base_ante = ante[ii % len(ante)]
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
    card['mult'] = f'x{mults[ii % len(mults)]}'
    card['ante1'] = antes[0]
    card['ante2'] = antes[1]
    card['ante3'] = antes[2]
    card['ante4'] = antes[3]
    if passer:
        if passer == 1:
            card['ante1'] = antes[1]
            card['ante2'] = antes[2]
            card['ante3'] = antes[3]
            card['ante4'] = 0
        if passer == 2:
            card['ante1'] = antes[1]
            card['ante2'] = antes[2]
            card['ante3'] = 0
            card['ante4'] = antes[3]
        if passer == 3:
            card['ante1'] = antes[1]
            card['ante2'] = 0
            card['ante3'] = antes[2]
            card['ante4'] = antes[3]
        if passer == 4:
            card['ante1'] = 0
            card['ante2'] = antes[1]
            card['ante3'] = antes[2]
            card['ante4'] = antes[3]
    card['compass_index'] = compass[ii % len(compass)]
    card['refill_delta'] = -1*resource[ii % len(resource)]
    resources = manual_resources[ii % len(manual_resources)]
    card['resource1'] = f'{resources[0]}x'
    card['resource2'] = f'{resources[1]}x'
    card['resource3'] = f'{resources[2]}x'
    card['resource4'] = f'{resources[3]}x'
    card['compass_rotation'] = compass_lookup[compass[ii % len(compass)]][0]
    card['compass_direction'] = compass_lookup[compass[ii % len(compass)]][1]
    dir = f'{builds[ii % len(builds)]+4} {compass_lookup[compass[ii % len(compass)]][1]}'
    card['compass_display'] = dir
    build = manual_builds[ii % len(manual_builds)]
    card['build'] = sum(1 for ii in build if ii > 1)
    card['build1'] = build[0]
    card['build2'] = build[1]
    card['build3'] = build[2]
    card['build4'] = build[3]
    card['id'] = f'F{ii+1:02}'
    cards.append(card)

headers = [
    'id',
    'market1',
    'market2',
    'market3',
    'market4',
    'ante1',
    'ante2',
    'ante3',
    'ante4',
    'mult',
    'refill_delta',
    'resource1',
    'resource2',
    'resource3',
    'resource4',
    'compass_index',
    'compass_direction',
    'compass_display',
    'compass_rotation',
    'build',
    'build1',
    'build2',
    'build3',
    'build4'
]
with open('../powergrid.csv','w', newline='') as write_handle:
    writer = csv.DictWriter(write_handle,headers)
    writer.writeheader()
    writer.writerows(cards)

city_max = 14
low_city = 0
low_turn = 0
low_index = 0
def calc_build(amounts):
    return len([x for x in amounts if x > 1])

manual_build_totals = [calc_build(x) for x in manual_builds]
manual_build_totals.sort()
while low_city < city_max:
    if low_index > 8:
        low_index = 0
    low_city += manual_build_totals[low_index]
    low_index += 1
    low_turn += 1

city_max = 14
high_city = 0
high_turn = 0
high_index = 23
while high_city < city_max:
    if high_index < 15:
        high_index = 23
    high_city += manual_build_totals[high_index]
    high_index -= 1
    high_turn += 1

hits = [0,0,0,0,0]
for market in manual_markets:
    for hit in market:
        hits[hit] += 1

print("==Automa deck stats==")
print("Market distribution")
print(hits)

hits = [0,0,0,0,0]
for res in manual_resources:
    for hit in res:
        hits[hit] += 1
print("Resource distribution")
print(hits)

hits = [0,0,0,0,0]
for builds in manual_builds:
    for hit in builds:
        hits[hit] += 1
print("build distribution")
print(hits)
print('\n\n')
print(f"The longest the automa will take is {low_turn} turns")
print(f"The shortest the automa will take is {high_turn} turns")

simulate.play_games(cards,GAMES_TO_SIMULATE)