"""Contains generic utilities and definitions used by the client, or server.
"""

import time
import logging
from pathlib import Path
from datetime import datetime

INVALID_TOKEN = "^\s+"
LOGGER_FORMAT = ""
LOGGING_LEVEL = logging.DEBUG
LOG_TO_CONSOLE = True

root_dir = Path(__file__).parent.parent
logging_folder = root_dir / Path("logs")
project_structure = {
    "logs": {},
    "settings.txt": "set token TOKEN_HERE"
}
default_settings = {
    "token": ""
}


def new_logger(logger_name: str, use_console: bool = False) -> logging.Logger:
    """Does all the handy-work to create a new logger. It uses the newly
    created logger file as the destination, with an optional destination
    of the console.

    :param logger_name: the name of the new logger
    :type logger_name: str
    :param use_console: whether or not to use the console as a handler
            alongisde the logging file.
    :type use_console: bool, defaults to False
    :return: the new logger
    :rtype: logging.Logger
    """

    destination_path = get_log_file()
    
    # Create the new Logger
    new_logger = logging.getLogger(logger_name)

    # Prevent adding the same handlers when they already exist.
    if len(new_logger.handlers) > 0:
        return new_logger

    new_logger.setLevel(LOGGING_LEVEL) 
    formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")

    # Create the File Handler
    file_handler = logging.FileHandler(destination_path)
    file_handler.setLevel(LOGGING_LEVEL)

    file_handler.setFormatter(formatter)
    new_logger.addHandler(file_handler)

    # Setup the handler for the Console
    if use_console is True:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOGGING_LEVEL)
        console_handler.setFormatter(formatter)

        new_logger.addHandler(console_handler)

    return new_logger


def get_date() -> str:
    """Retrieves the current date.

    :return: the current date
    :rtype: str
    """

    return datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")


def get_time() -> str:
    """Retrieves the current time.

    :return: the current time
    :rtype: str
    """

    return datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")


def get_log_file() -> Path:
    """Returns the Path of the current logfile. Note: If a session lasts longer
    than a day, this will return the wrong logfile.
    """

    return logging_folder / Path(get_date() + ".txt")


def iter_structure(root: Path, structure: dict) -> (Path, bool):
    """Iterates through a given structure and yields the path
    to a folder, or file based off a root directory.

    :param root: the root directory to start based off
    :type root: Path
    :param structure: the dictionary to parse
    :type structure: dict
    :return: a Path to a file or folder, and whether or not
            it is a folder
    :rtype: Path, bool
    """

    folders = [(structure, root)]

    while len(folders) > 0:
        sub_folder, path_to = folders.pop(0)

        # Yield paths and add more sub-folders.
        for name, descendants in sub_folder.items():
            new_path_to = path_to / Path(name)
            is_folder = isinstance(descendants, dict)

            # New folder to loop through.
            if is_folder:
                folders.append((descendants, new_path_to))
            else:  # Usually for returning text for a file.
                is_folder = descendants

            yield new_path_to, is_folder


def initialize(head_directory: Path = root_dir):
    """Initializes the directory structure and other necessities inside of
    a root directory.
    """

    logger = new_logger("pycord-main", use_console=LOG_TO_CONSOLE)

    for path, is_dir in iter_structure(head_directory, project_structure):
        if path.exists() is True:
            continue

        if is_dir is True:
            path.mkdir()
        elif isinstance(is_dir, str):
            with open(path, "w+") as new_file:
                new_file.write(is_dir)

    logger.info("Completed tree creation.")
