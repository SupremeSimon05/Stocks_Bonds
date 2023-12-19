import os, shutil, select, sys
from to_ascii import to_ascii

def get_terminal_size():
    try:
        columns, rows = shutil.get_terminal_size()
    except AttributeError:
        # Fallback for Python versions < 3.3
        _, columns, _, rows = os.get_terminal_size()
    return columns, rows

def printing():
    cols, rows = get_terminal_size()
    to_ascii("good.gif", "Alec_Bird.png", cols, rows-2, True, ASCII_DENSITY="█Ñ")