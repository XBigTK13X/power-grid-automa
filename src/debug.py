import os

DEBUG_GAME = False
DEBUG_SIM = False
DEBUG_RESULT = False
LOG_FILES = False

os.makedirs("./log", exist_ok=True)

log_buffer = []


def game(message):
    if DEBUG_GAME:
        print(message)
    if LOG_FILES:
        log_buffer.append(str(message))


def sim(message):
    if DEBUG_SIM:
        print(message)
    if LOG_FILES:
        log_buffer.append(str(message))


def result(message):
    if DEBUG_RESULT:
        print(message)
    if LOG_FILES:
        log_buffer.append(str(message))


def flush(log_index):
    global log_buffer
    if LOG_FILES and log_buffer:
        index_str = f"{log_index:03d}"
        dir_first = index_str[0]
        dir_second = index_str[1]
        target_dir = os.path.join("./log", dir_first, dir_second)
        os.makedirs(target_dir, exist_ok=True)

        file_path = os.path.join(target_dir, f"{log_index}.log")
        with open(file_path, "w") as write_handle:
            write_handle.write("\n".join(log_buffer) + "\n")
    log_buffer.clear()


def save_summary(summary_text, filename="summary.txt"):
    target_path = os.path.join("./log", filename)
    with open(target_path, "w") as write_handle:
        write_handle.write(summary_text)
