"""This file handles the settings of the Discord client.
"""

import logging
from pathlib import Path

valid_actions = ["set"]
root_dir = Path(__file__).parent.parent
settings_logger = logging.getLogger("pycord_settings")


def error(line_number: int, error_message: str):
    """Spits out an error message on the specified line number.

    :param line_number: the line the error occured on
    :type line_number: int
    :param error_message: the error message
    :type error_message: str
    """

    print(f"Line {line_number}: {error_message}")


def get_settings_file() -> Path:
    """Attempts to search for the settings file somewhere in the project's
    directory.

    :return: the path to the settings file
    :rtype: Path, None
    """

    file_path = root_dir / Path("settings.txt")

    if file_path.exists() is True:
        return file_path
    else:
        return None


def extract_settings(settings_file: Path, defaults: dict) -> dict:
    """Extracts the settings from a settings file, and returns
    it in the form of a dictionary.

    :param settings_file: the path to the settings file
    :type settings_file: Path
    :param defaults: the default settings
    :type defaults: dict
    :return: the parsed settings
    :rtype: dict
    """

    new_settings = defaults.copy()

    # No settings to parse
    if settings_file.exists() is False:
        logger.info("No settings file. Loading defaults.")
        return defaults

    # Extract the settings
    with open(settings_file, "r") as settings_buffer:
        settings = settings_buffer.readlines()

        for index in range(len(settings)):
            setting = settings[index].strip()

            line = index + 1
            tokens = setting.split(" ")

            # Handles no arguments for the action or no value for the action.
            if len(tokens) == 1:
                error(line, f"No argument(s) for '{tokens[0]}'")
                break
            elif len(tokens) == 2:
                error(line, f"No value for '{tokens[1]}'")
                break

            action = tokens[0]
            setting_name = tokens[1]
            value = "".join(tokens[2:])

            # Handles invalid actions.
            if action not in valid_actions:
                error(line, f"'{action}' is not a valid action.")
                break

            #  Assigns new values for defaults settings.
            try:
                default_type = type(defaults[setting_name])
                new_settings[setting_name] = default_type(value)
            except KeyError:
                error(line, f"No setting named '{setting_name}'")
                break
            except ValueError:
                error(line, f"Invalid type. Type should be {default_type}")
                break

    return new_settings
