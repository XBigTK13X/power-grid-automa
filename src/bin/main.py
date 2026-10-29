import src.board
import src.debug as debug
import src.generate as generate
import src.simulate as simulate

GAMES_TO_SIMULATE = 10000
PLAYER_COUNT = 3

if GAMES_TO_SIMULATE > 1:
    debug.DEBUG_SIM = False
    debug.DEBUG_GAME = False
    debug.DEBUG_RESULT = False
else:
    debug.DEBUG_SIM = True
    debug.DEBUG_GAME = True
    debug.DEBUG_RESULT = True

debug.LOG_FILES = True
MAP = src.board.germany

cards = generate.create_cards()
generate.write_cards_to_csv(cards)
simulate.play_games(cards, GAMES_TO_SIMULATE, MAP, PLAYER_COUNT)
