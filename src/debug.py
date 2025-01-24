DEBUG_GAME=False
DEBUG_SIM=False
DEBUG_RESULT=False
LOG_FILES=False

import os

os.makedirs('./log',exist_ok=True)

log_file_content = ''

def game(message):
    global log_file_content
    if DEBUG_GAME:
        print(message)
    log_file_content += f'{message}\n'

def sim(message):
    global log_file_content
    if DEBUG_SIM:
        print(message)
    log_file_content += f'{message}\n'

def result(message):
    global log_file_content
    if DEBUG_RESULT:
        print(message)
    log_file_content += f'{message}\n'


def flush(log_index):
    global log_file_content
    if LOG_FILES:
        with open(f'./log/sim-{log_index}.log','w') as write_handle:
            write_handle.write(log_file_content)
    log_file_content = ''