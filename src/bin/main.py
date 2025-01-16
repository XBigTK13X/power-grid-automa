import src.debug as debug
debug.DEBUG_SIM = True
debug.DEBUG_GAME = True

import src.generate as generate
import src.simulate as simulate
import src.board

GAMES_TO_SIMULATE = 1
MAP = src.board.united_states_of_america
PLAYER_COUNT = 3

cards = generate.create_cards()
generate.write_cards_to_csv(cards)
simulate.play_games(cards, GAMES_TO_SIMULATE, MAP, PLAYER_COUNT)