"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_standard_tap_tests

from tap_zohosprints.tap import TapZohoSprints

SAMPLE_CONFIG = {
    "api_url": os.environ["TAP_ZOHOSPRINTS_API_URL"],
    "oauth_url": os.environ["TAP_ZOHOSPRINTS_OAUTH_URL"],
    "client_id": os.environ["TAP_ZOHOSPRINTS_CLIENT_ID"],
    "client_secret": os.environ["TAP_ZOHOSPRINTS_CLIENT_SECRET"],
    "refresh_token": os.environ["TAP_ZOHOSPRINTS_REFRESH_TOKEN"],
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapZohoSprints, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
