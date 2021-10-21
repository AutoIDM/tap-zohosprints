"""ZohoSprints tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_zohosprints.streams import (
    TeamsStream,
    MetaProjectsStream,
    ProjectsStream,
    EpicsStream,
)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    TeamsStream,
    MetaProjectsStream,
    ProjectsStream,
    EpicsStream,
]


class TapZohoSprints(Tap):
    """ZohoSprints tap class."""
    name = "tap-zohosprints"

    config_jsonschema = th.PropertiesList(
        th.Property("api_url", th.StringType, required=True), #Example https://sprintsapi.zoho.com/zsapi
        th.Property("oauth_url", th.StringType, required=True), #Example https://accounts.zoho.com/oauth/v2/token
        th.Property("client_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True),
        th.Property("refresh_token", th.StringType, required=True),
        th.Property("start_date", th.DateTimeType),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
