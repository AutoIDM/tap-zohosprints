"""Stream type classes for tap-zohosprints."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zohosprints.client import ZohoSprintsStream

# TODO: Delete this is if not using json files for schema definition
#SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class TeamsStream(ZohoSprintsStream):
    """Define custom stream."""
    name = "teams"
    path = "/teams/"
    #primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("ownerTeamIds", th.ArrayType(th.StringType)),
        th.Property("defaultPortalId", th.StringType),
        th.Property("myTeamId", th.StringType),
        th.Property("portals", th.ArrayType(th.ObjectType(
                                                th.Property("teamName", th.StringType),
                                                th.Property("isShowTeam", th.BooleanType),
                                                th.Property("orgName", th.StringType),
                                                th.Property("portalOwner", th.StringType),
                                                th.Property("type", th.IntegerType),
                                                th.Property("zsoid", th.StringType),
            ))),
        th.Property("status", th.StringType),
    ).to_dict()
