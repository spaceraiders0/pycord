import sys
from pathlib import Path

modules = Path(__file__).parent.parent / Path("src")
sys.path.append(str(modules))

import authentication

TEST_TOKEN = "mfa.FJdsjj5JDWWHDWDED-0WEDJWsd93hu8S8dsuhaq9SWQ8YDQASQ3JWHJQJH"


def test_validation():
    """Tests the authentication methods.
    """

    assert authentication.validate_token("mfa.ThisIsAValidToken") is True
    assert authentication.validate_token("foo") is False
    assert authentication.validate_token("") is False
    assert authentication.validate_token("      ") is False
