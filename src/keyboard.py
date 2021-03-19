"""This file controls the keyboard of Pycord.
"""

import curses

stdscr = curses.initscr()
stdscr.keypad(1)
curses.cbreak()
curses.noecho()

is_alt = False

try:
    while True:
        new_key = stdscr.getch()

        if new_key == 27:
            break
finally:
    curses.endwin()
