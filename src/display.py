"""This contains methods used by the client to display window panes.
"""

import time
import curses
import shutil
import utilities
from threading import Thread

stdscr = curses.initscr()
curses.start_color()
curses.cbreak()
stdscr.keypad(1)
curses.noecho()
curses.curs_set(0)

last_y = 0
columns = []
term_size = shutil.get_terminal_size()

logger = utilities.new_logger("pycord-display")


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

    last_x = 0

    def __init__(self, end: int, *windows):
        Window.last_y = 0

        self.windows = []

        for window in windows:
            window.parent = self
            self.windows.append(window)

        self.start = Column.last_x 
        self.end = round(get_scale(end, term_size.columns))
        self.relative_end = self.end - self.start

        # This will make the next column start after the previous one.
        Column.last_x = self.end


class Window:
    """A window is a display source that goes inside of columns. Windows display
    information from a list. Each entry in a list corresponds to a line in the
    window. Windows are stacked on top of each other vertically, similar to how
    columns are positioned next to each other.
    """

    last_y = 0

    def __init__(self, source: list, end: int, title="", selected=False):
        # Dimensions
        self.start = Window.last_y
        self.end = round(get_scale(end, term_size.lines))
        self.relative_end = self.end - self.start

        # Draw information
        self.selected = selected
        self.title = title
        self.source = source
        self.draw_range = range(0, self.relative_end)
        self.message_selection = range(0, 1)

        # Other
        self.parent: Column = None
        self.textbox: curses.Window = None
        self.frame: curses.Window = None

        # This will make the next window start after the previous one.
        Window.last_y = self.end

    def update(self):
        """Empties the window and redraws the information inside of it.
        """

        # Draws the messages.
        line = 0
        window = self.textbox
        window.erase()

        try:
            draw_start, draw_stop = self.draw_range.start, self.draw_range.stop

            for message in self.wrap_source()[draw_start:draw_stop]:
                if line in self.message_selection:
                    window.addstr(line, 0, message, curses.A_REVERSE)
                else:
                    window.addstr(line, 0, message)
                line += 1
        except curses.error:
            pass

    def redraw(self):
        """Redraws the border of the frame.
        """

        if self.frame is not None:
            self.frame.erase()
        
        if self.textbox is not None:
            self.textbox.erase()

        frame, textbox = window.create_display()
        window.frame = frame
        window.textbox = textbox
        stdscr.refresh()
        frame.refresh()
        window.update()
        textbox.refresh()

    def create_display(self) -> (curses.window, curses.window):
        """Creates a new window frame, and a textbox inside of it.

        :param size: the size of the window
        :type size: tuple
        :param position: the position of the window
        :type position: tuple
        :return: a window frame, and text box
        :rtype: tuple
        """

        size_y, size_x = self.relative_end, self.parent.relative_end
        position_y, position_x = self.start, self.parent.start

        window_frame = curses.newwin(size_y, size_x, position_y, position_x)
        window_frame.border(0, 0, 0, 0)

        if self.selected is True:
            window_frame.addstr(0, 1, self.title, curses.A_BLINK)
        else:
            window_frame.addstr(0, 1, self.title)

        window_textbox = curses.newwin(size_y - 2, size_x - 2,
                                       position_y + 1, position_x + 1)

        return window_frame, window_textbox

    def wrap_source(self) -> list:
        """Returns a version of self.source where each line that reaches a line
        feed character, or goes beyond the size of the box, is separated into
        it's own element.

        :return: a list of the wrapped source
        :rtype: list
        """

        stop_index = self.textbox_size[1]
        new_lines = []

        for line in self.source:
            built_line = ""
            line_width = 0

            for character in line:
                # Effectively "wraps" words", but across different lines.
                if line_width == stop_index:
                    new_lines.append(built_line)
                    built_line = ""
                    line_width = 0

                built_line += character
                line_width += 1
            else:
                new_lines.append(built_line)

        return new_lines

    def move(self, change: int):
        """Moves the cursor down or up. Will also shift the drawing range if
        the cursor is on the edges.

        :param change: the direction to move
        :type change: int
        """

        selection = self.message_selection
        next_start = selection.start + change
        next_end = selection.stop + change

        if 0 <= next_start and next_end <= len(self.wrap_source()):
            self.message_selection = range(next_start, next_end)

    @property
    def maximum_characters(self):
        """The maximum number of characters this window can hold.

        :return: the maximum number of characters this window can hold
        :rtype: int
        """

        y, x = self.textbox_size

        return y * x

    @property
    def textbox_size(self):
        """Returns the dimensions of the textbox inside of the textbox.

        :return: the dimensions of the textbox
        :rtype: tuple
        """

        return (self.relative_end - 2, self.parent.relative_end - 2)

    @property
    def window_size(self):
        """Returns the dimensions of the window

        :return: the dimensions of the window
        :rtype: tuple
        """

        return (self.relative_end, self.parent.relative_end)

# Window sizes are not 100% accurate, but they should do for now.
my_screen = Screen(
    Column(
        10,
        Window([], 25, title="PMs"),
        Window([], 50, title="Servers"),
        Window([], 100, title="Channels"),
    ),
    Column(
        90,
        Window([], 95, "Message History"),
        Window([], 100)
    ),
    Column(
        100,
        Window(["foo" for n in range(40)], 100, title="Users", selected=True)
    )
)


try:
    for column_index in range(0, len(my_screen.columns)):
        column: Column = my_screen.columns[column_index]

        for window_index in range(0, len(column.windows)):
            window: Window = column.windows[window_index]
            window.redraw()
#             window: Window = column.windows[window_index]
# 
#             frame, textbox = window.create_display()
#             window.frame = frame
#             window.textbox = textbox
#             stdscr.refresh()
#             frame.refresh()
#             window.update(textbox)
#             textbox.refresh()

    # Draw Curses windows.
    while True:
        next_char = stdscr.getch()
        # Ideas:
        # Only call refresh on windows that need it.
        # Have *client* commands, and *server* commands.
        window: window = my_screen.columns[2].windows[0]
        
        if next_char == ord("j"):
            window.move(1)
            window.update()
            window.textbox.refresh()
        elif next_char == ord("k"):
            window.move(-1)
            window.update()
            window.textbox.refresh()
        elif next_char == 27:
            for column in my_screen.columns:
                # This code will require making an entirely new frame.
                # I need a way of universally controlling these.
                last_window = column.windows[-1]
                last_window.relative_end -= 5
                last_window.frame.refresh()
finally:
    curses.endwin()
