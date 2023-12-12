import os
import shutil
from to_ascii import to_ascii

def get_terminal_size():
    try:
        columns, rows = shutil.get_terminal_size()
    except AttributeError:
        # Fallback for Python versions < 3.3
        _, columns, _, rows = os.get_terminal_size()
    return columns, rows
cols, rows = get_terminal_size()
print(cols, rows)
to_ascii("Alec_Bird.png", cols, rows-1, False)