"""Exposes functions to handle authentication for the server.
"""

import re
import settings
import utilities
from utilities import INVALID_TOKEN
from pathlib import Path

root_dir = Path(__file__).parent.parent


def validate_token(token: str) -> bool:
    """Validates the token passed into it.

    :param token: the token to validate
    :type token: str
    :return: whether or not the token is valid
    :rtype: bool
    """

    # The qualifications for an "invalid" token
    if len(token) == 0 or re.match(INVALID_TOKEN, token) is not None \
                       or token.startswith("mfa.") is False:
        return False
    else:
        return True


def extract_token(settings_file: Path) -> str:
    """Extracts the token from the provided settings file.

    :param settings_file: the settings file to extract the token from
    :type settings_file: Path
    :return: the extracted token
    :rtype: str
    """

    default_settings = utilities.default_settings
    discord_token = settings.extract_settings(settings_file, default_settings)["token"]

    if validate_token(discord_token) is False:
        return ""
    else:
        return discord_token
