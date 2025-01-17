import src.debug as debug
debug.DEBUG_SIM = False
debug.DEBUG_GAME = False
debug.DEBUG_RESULT = True
GAMES_TO_SIMULATE = 100
PLAYER_COUNT = 3
import src.board
MAP = src.board.united_states_of_america

import src.generate as generate
import src.simulate as simulate

cards = generate.create_cards()
generate.write_cards_to_csv(cards)
simulate.play_games(cards, GAMES_TO_SIMULATE, MAP, PLAYER_COUNT)