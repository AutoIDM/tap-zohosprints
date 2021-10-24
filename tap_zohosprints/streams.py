"""Stream type classes for tap-zohosprints."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zohosprints.client import ZohoSprintsStream
from tap_zohosprints.client import ZohoSprintsPropsStream
import copy
import requests

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class TeamsStream(ZohoSprintsStream):
    """Define custom stream."""
    name = "team"
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
    
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id":record["myTeamId"]
        }

class MetaProjectsStream(ZohoSprintsStream):
    """Went with this approach as Items sometimes had extra data in
    the project details page. Meta in this case really means useless data. 

    Tradeoff seemed reasonable for easier to understand code. 
    """
    name = "meta_project"
    path = "/team/{team_id}/projects/?action=allprojects&index=1&range=10"
    parent_stream_type = TeamsStream
    primary_keys = "project_id" 
    replication_key = None
    schema = th.PropertiesList(
            th.Property("project_id", th.StringType),
            th.Property("team_id", th.StringType),
            ).to_dict()
    #TODO Pagination

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Only need the project_ids list from the projects stream"
        """
        #TODO should be able to do this with jsonpath
        for row in self.request_records(context):
            row = self.post_process(row, context)
            for project in row.get("projectIds"):
                #team_id here is a leaky abstraction, seems like a decent tradeoff
                data = {"project_id":project, "team_id":context.get("team_id")}
                yield data

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return record

class ProjectsStream(ZohoSprintsStream):
    """ProjectStream"""
    name = "project"
    path = "/team/{team_id}/projects/{project_id}/?action=details"
    parent_stream_type =MetaProjectsStream
    primary_keys = ["$.projectIds[0]"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "project.json"

    #TODO get_records needs to make the Project Details object useful
    #Project Details should be useful, so decided to transform the data slightly
    #To align properties with their data elements. Left the raw object as well
    #Just in case this parsing isn't exactly what is wanted later on
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id":context["team_id"],
            "project_id":context["project_id"],
        }

class EpicsStream(ZohoSprintsPropsStream):
    """Epics"""
    name = "epic"
    path = "/team/{team_id}/projects/{project_id}/epic/?action=data&index=1&range=10"
    parent_stream_type = ProjectsStream
    primary_keys = ["epic_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "epic.json"
    
    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.
        """
        for row in self.request_records(context):
            row = self.post_process(row, context)
            yield row
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        #Create a record object
        yield from self.property_unfurler(response=response,
                prop_key="epic_prop",
                ids_key="epicIds",
                jobj_key="epicJObj",
                primary_key_name="epic_id")


class SprintsStream(ZohoSprintsStream):
    """Sprints"""
    name = "sprint"
    path = "/team/{team_id}/projects/{project_id}/sprints/?action=data&index=1&range=10&type=[1,2,3,4]"
    parent_stream_type = ProjectsStream
    primary_keys = ["$.sprintIds[0]"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "sprint.json"

class BacklogsStream(ZohoSprintsStream):
    """Backlogs"""
    name = "backlog"
    path = "/team/{team_id}/projects/{project_id}/?action=getbacklog"
    parent_stream_type = ProjectsStream
    primary_keys = ["$.backlogId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "backlog.json"
    
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "team_id":context["team_id"],
            "project_id":context["project_id"],
            "backlog_id":record["backlogId"],
        }

class BacklogItemsStream(ZohoSprintsStream):
    """Items"""
    name = "items_backlog"
    path = "/team/{team_id}/projects/{project_id}/sprints/{backlog_id}/item/?action=sprintitems&index=1&range=10&subitem=true"
    parent_stream_type = BacklogsStream
    primary_keys = ["$.itemIds[0]"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "item.json"

#TODO need to get Items Individually due to Custom Fields
