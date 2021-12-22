"""Stream type classes for tap-zohosprints."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zohosprints.client import ZohoSprintsStream
from tap_zohosprints.client import ZohoSprintsPropsStream
from tap_zohosprints.client import property_unfurler
import copy
import requests

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class TeamsStream(ZohoSprintsStream):
    """Define custom stream."""

    name = "team"
    path = "/teams/"
    primary_keys = ["ownerTeamIds"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("ownerTeamIds", th.ArrayType(th.StringType)),
        th.Property("defaultPortalId", th.StringType),
        th.Property("myTeamId", th.StringType),
        th.Property(
            "portals",
            th.ArrayType(
                th.ObjectType(
                    th.Property("teamName", th.StringType),
                    th.Property("isShowTeam", th.BooleanType),
                    th.Property("orgName", th.StringType),
                    th.Property("portalOwner", th.StringType),
                    th.Property("type", th.IntegerType),
                    th.Property("zsoid", th.StringType),
                )
            ),
        ),
        th.Property("status", th.StringType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {"team_id": record["portals"][0]["zsoid"]}


class MetaProjectsStream(ZohoSprintsPropsStream):
    """Went with this approach as Items sometimes had extra data in
    the project details page. Meta in this case really means useless data.

    Tradeoff seemed reasonable for easier to understand code.
    """

    name = "meta_project"
    path = "/team/{team_id}/projects/?action=allprojects"
    parent_stream_type = TeamsStream
    primary_keys = ["project_id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("project_id", th.StringType),
        th.Property("team_id", th.StringType),
    ).to_dict()
    # TODO Pagination
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="project_prop",
            ids_key="projectIds",
            jobj_key="projectJObj",
            primary_key_name="project_id",
        )

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {"project_id": record["project_id"], "team_id": context["team_id"]}


class ProjectsStream(ZohoSprintsPropsStream):
    """ProjectStream"""

    name = "project"
    path = "/team/{team_id}/projects/{project_id}/?action=details"
    parent_stream_type = MetaProjectsStream
    primary_keys = ["project_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "project.json"

    # TODO can we get rid of this?
    # Needed as this endpoint doesn't take an index/range as other PropsStreams do
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["index"] = next_page_token
        # if self.replication_key:
        # params["sort"] = "asc"
        # params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="project_prop",
            ids_key="projectIds",
            jobj_key="projectJObj",
            primary_key_name="project_id",
        )

    # TODO get_records needs to make the Project Details object useful
    # Project Details should be useful, so decided to transform the data slightly
    # To align properties with their data elements. Left the raw object as well
    # Just in case this parsing isn't exactly what is wanted later on
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id": context["team_id"],
            "project_id": record["project_id"],
        }


class TagsStream(ZohoSprintsPropsStream):
    """TagsStream"""

    name = "tag"
    path = "/team/{team_id}/tags/?action=data&index=1&range=1000"
    parent_stream_type = TeamsStream
    primary_keys = ["tagId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "tag.json"

    # TODO can we get rid of this?
    # Needed as this endpoint doesn't take an index/range as other PropsStreams do
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["index"] = next_page_token
        # if self.replication_key:
        # params["sort"] = "asc"
        # params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="zsTag_prop",
            ids_key="zsTagIds",
            jobj_key="zsTagJObj",
            primary_key_name="tagId",
        )


class EpicsStream(ZohoSprintsPropsStream):
    """Epics"""

    name = "epic"
    path = "/team/{team_id}/projects/{project_id}/epic/?action=data"
    parent_stream_type = ProjectsStream
    primary_keys = ["epic_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "epic.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="epic_prop",
            ids_key="epicIds",
            jobj_key="epicJObj",
            primary_key_name="epic_id",
        )


class SprintsStream(ZohoSprintsPropsStream):
    """Sprints"""

    name = "sprint"
    path = "/team/{team_id}/projects/{project_id}/sprints/?action=data&type=[1,2,3,4]"
    parent_stream_type = ProjectsStream
    primary_keys = ["sprint_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "sprint.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="sprint_prop",
            ids_key="sprintIds",
            jobj_key="sprintJObj",
            primary_key_name="sprint_id",
        )

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id": context["team_id"],
            "project_id": context["project_id"],
            "sprint_id": record["sprint_id"],
        }


class BacklogsStream(ZohoSprintsStream):
    """Backlogs"""

    name = "backlog"
    path = "/team/{team_id}/projects/{project_id}/?action=getbacklog"
    parent_stream_type = ProjectsStream
    primary_keys = ["backlogId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "backlog.json"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id": context["team_id"],
            "project_id": context["project_id"],
            "backlog_id": record["backlogId"],
        }


class BacklogItemsStream(ZohoSprintsPropsStream):
    """Items"""

    name = "items_backlog"
    path = "/team/{team_id}/projects/{project_id}/sprints/{backlog_id}/item/?action=sprintitems&subitem=true"
    parent_stream_type = BacklogsStream
    primary_keys = ["item_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "item.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="item_prop",
            ids_key="itemIds",
            jobj_key="itemJObj",
            primary_key_name="item_id",
        )

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id": context["team_id"],
            "project_id": context["project_id"],
            "backlog_id": context["backlog_id"],
            "item_id": record["item_id"],
        }


class BacklogItemDetailsStream(ZohoSprintsPropsStream):
    """Items"""

    # TODO change this name
    name = "item_details_backlog"
    path = "/team/{team_id}/projects/{project_id}/sprints/{backlog_id}/item/{item_id}/?action=details"
    parent_stream_type = BacklogItemsStream
    primary_keys = ["item_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "item.json"

    # TODO this is duplicated for ProjectDetails as well
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["index"] = next_page_token
        # if self.replication_key:
        # params["sort"] = "asc"
        # params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="item_prop",
            ids_key="itemIds",
            jobj_key="itemJObj",
            primary_key_name="item_id",
        )


# TODO need to get Items Individually due to Custom Fields


class SprintItemsStream(ZohoSprintsPropsStream):
    """Items"""

    name = "items_sprint"
    path = "/team/{team_id}/projects/{project_id}/sprints/{sprint_id}/item/?action=sprintitems&subitem=true"
    parent_stream_type = SprintsStream
    primary_keys = ["item_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "item.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="item_prop",
            ids_key="itemIds",
            jobj_key="itemJObj",
            primary_key_name="item_id",
        )

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id": context["team_id"],
            "project_id": context["project_id"],
            "sprint_id": context["sprint_id"],
            "item_id": record["item_id"],
        }


class SprintItemDetailsStream(ZohoSprintsPropsStream):
    """Items"""

    # TODO change this name
    name = "items_sprint"
    path = "/team/{team_id}/projects/{project_id}/sprints/{sprint_id}/item/{item_id}/?action=details"
    parent_stream_type = SprintItemsStream
    primary_keys = ["item_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "item.json"

    # TODO this is duplicated for ProjectDetails as well
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["index"] = next_page_token
        # if self.replication_key:
        # params["sort"] = "asc"
        # params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="item_prop",
            ids_key="itemIds",
            jobj_key="itemJObj",
            primary_key_name="item_id",
        )


class SprintUsers(ZohoSprintsPropsStream):
    """Sprint User Stream"""

    name = "sprint_user"
    path = "/team/{team_id}/projects/{project_id}/sprints/{sprint_id}/users/"
    parent_stream_type = SprintsStream
    primary_keys = ["user_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "sprint_user.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="user_prop",
            ids_key="userIds",
            jobj_key="userJObj",
            primary_key_name="user_id",
        )

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        return {"action": "alldata"}


class ProjectUsers(ZohoSprintsPropsStream):
    """Project User Stream"""

    name = "project_user"
    path = "/team/{team_id}/projects/{project_id}/users/?action=data"
    parent_stream_type = ProjectsStream
    primary_keys = ["userId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "project_user.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="user_prop",
            ids_key="userIds",
            jobj_key="userJObj",
            primary_key_name="userId",
        )


class LogHours(ZohoSprintsPropsStream):
    """Log Hours Stream"""

    name = "log_hour"
    path = "/team/{team_id}/projects/{project_id}/sprints/{sprint_id}/timesheet/?action=logitems&listviewtype=0"
    parent_stream_type = SprintsStream
    primary_keys = ["tLogId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "log_hour.json"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Create a record object
        yield from property_unfurler(
            response=response,
            prop_key="log_prop",
            ids_key="logIds",
            jobj_key="logJObj",
            primary_key_name="tLogId",
        )
