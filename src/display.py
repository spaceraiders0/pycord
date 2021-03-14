"""This contains methods used by the client to display window panes.
"""

import time
import curses
import shutil
import utilities

stdscr = curses.initscr()
curses.nocbreak()
curses.noecho()

last_start = 0 
columns = []
term_size = shutil.get_terminal_size()

logger = utilities.new_logger("pycord-display")
logger.debug(f"Terminal Dimensions: X: {term_size.columns}, Y: {term_size.lines}\n")


def get_scale(percent: float, maximum: float) -> int:
    """Returns n percent of a maximum value.

    :param percent: the percent of a maximum to find
    :type percent: float
    :param maximum: the highest possible value the scale is based on
    :type maximum: float
    """

    return (maximum / 100) * percent

class Screen:
    """The Screen is a container for columns. It contains methods, and fields
    that are utilized, or read by individual columns.
    """

    def __init__(self, *columns):
        width, height = shutil.get_terminal_size() 

        self.columns = [*columns]
        self.column_count = len(columns)
        self.used_columns = len([column for column in columns if len(column.windows) > 0])
        self.width = width
        self.height = height

    def balance(self):
        """Makes each column contained inside of it take up (roughly) even
        portion of the screen relative to the other columns.
        """

        base_width = round(self.width / self.used_columns)
        start, end = 0, get_scale(base_width, self.width)

        for index in range(0, len(self.columns)):
            column = self.columns[index]
            new_width = round(get_scale(base_width * (index + 1), self.width))
            column.start = start
            column.end = new_width
            start = new_width


class Column:
    """A column is a container for windows.

    Columns take up a portion of the terminal's width. When a column is made,
    It will begin at the end of the previous column. It will end at a given
    ending percent.
    """

    def __init__(self, end: int, *windows):
        global last_start

        terminal_width = shutil.get_terminal_size().columns
        self.start = last_start
        self.end = round(get_scale(end, terminal_width))
        self.relative_end = self.end - self.start
        self.windows = [*windows]

        # This will make the next column start after the previous one.
        last_start = self.end


class Window:
    """A window is a display source that goes inside of columns. Windows display
    information from a list. Each entry in a list describes
    """

    pass


my_screen = Screen(
    Column(100, 1)
)

try:
    # Draw Curses windows.
    while True:
        for index in range(0, len(my_screen.columns)):
            column: Column = my_screen.columns[index]
            start, stop = column.start, column.end
            new_window = curses.newwin(term_size.lines, column.relative_end, 0, start)
            new_window.border(0, 0, 0, 0)
            new_window.refresh()

        time.sleep(1)
finally:
    curses.endwin()


#my_screen.balance()
