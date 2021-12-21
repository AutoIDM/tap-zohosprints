"""Tests standard tap features using the built-in SDK tests library."""

import datetime
from pathlib import Path
import os
import pytest
import responses
import requests

from singer_sdk.testing import get_standard_tap_tests
from tap_zohosprints.client import (
    ZohoSprintsPropsStream,
    ZohoSprintsStream,
    property_unfurler,
)

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


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_property_unfurler(mocked_responses):
    tag_json = ""
    with open(Path(__file__).parent / Path("tag_property_unfurl.json")) as tag:
        tag_json = tag.read()

    mocked_responses.add(
        responses.GET,
        "https://autoidm.com",
        body=tag_json,
        status=200,
        content_type="application/json",
    )
    resp = requests.get("https://autoidm.com")
    assert resp.status_code == 200

    unfurled = property_unfurler(
        response=resp,
        prop_key="zsTag_prop",
        ids_key="zsTagIds",
        jobj_key="zsTagJObj",
        primary_key_name="tagId",
    )
    output = None
    for data in unfurled:
        output = data
    assert output == {
        "next": False,
        "hasItemTagPermission": True,
        "ItemTagCount": 25,
        "userDisplayName": {},
        "zsuserIdvsZUID": {},
        "status": "success",
        "record": {
            "tagId": "114398000000007021",
            "createdBy": "114398000000002003",
            "colorCode": "#f17f23",
            "tagName": "dsaf",
        },
        "tagId": "114398000000007021",
    }
