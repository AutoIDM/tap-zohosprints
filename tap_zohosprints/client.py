"""REST client handling, including ZohoSprintsStream base class."""

import copy
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.authenticators import APIAuthenticatorBase, SimpleAuthenticator, OAuthAuthenticator, OAuthJWTAuthenticator
from singer_sdk.streams import RESTStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class ZohoSprintsAuthenticator(OAuthAuthenticator):

    @property
    def oauth_request_body(self) -> dict:
        return {
            'grant_type': 'refresh_token',
            'redirect_uri': "http://localhost",#not needed for our use, but api requires it
            'client_id': self.config["client_id"],
            'client_secret': self.config["client_secret"],
            'refresh_token': self.config["refresh_token"],
        }

class ZohoSprintsStream(RESTStream):
    """ZohoSprints stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    records_jsonpath = "$"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.next_index"  # Or override `get_next_page_token`.

    _LOG_REQUEST_METRIC_URLS: bool = True

    @property
    @cached
    def authenticator(self) -> ZohoSprintsAuthenticator:
        """Return a new authenticator object."""
        return ZohoSprintsAuthenticator(stream=self, auth_endpoint=self.config["oauth_url"])

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        # TODO: If pagination is required, return a token which can be used to get the
        #       next page. If this is the final page, return "None" to end the
        #       pagination loop.
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
        else:
            next_page_token = response.headers.get("X-Next-Page", None)

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # TODO: Delete this method if not needed.
        return row

class ZohoSprintsPropsStream(ZohoSprintsStream):
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""

        #Raise if not implemented
        raise(NotImplementedError)
        #Create a record object
        #json = response.json()
        #epic_props: Dict = json.get("epic_prop")
        #epic_ids: List = json.get("epicIds")
        #for epic_id in epic_ids:
            #record = {}
            #epic_prop_values: List = json["epicJObj"][epic_id]
            #for property_name, property_index in epic_props.items():
                #record[property_name] = epic_prop_values[property_index]
            #return_object: Dict = copy.deepcopy(json)
            #return_object["epic_id"] = epic_id
            #return_object.pop("epic_prop")
            #return_object.pop("epicIds")
            #return_object.pop("epicJObj")
            #return_object["record"] = record
            #self.logger.info(return_object)
            #yield return_object

    #Should add a few tests here
    def property_unfurler(self, 
            response: requests.Response,
            prop_key: str,
            ids_key: str,
            jobj_key: str,
            primary_key_name: str,
            ) -> Iterable[dict]:
        """
        Zohosprints embeds data inside of a JObj key.
        
        Example of a response like this is https://sprints.zoho.com/apidoc.html#Getallepics
        epic_prop has the properties
        epicJObj has all the data

        While one option would be to leave data in this format, we decided not 
        to because: 
        1) Matching the _prop and JObj properties has to happen somewhere 
        downstream, doing this mapping in your downstream system is painful and requires more 
        knowledge then you'd like to have to have about the source data.

        2)we have to run discovery to populate the proper schemas 
        when there's custom fields that can be added to epic_prop (Scenario is
        most likely for Items not Epics), this means we have to parse through
        this data anyways, so why not also populate a record object that's
        much easier for us humans to use!

        Embded this data under a "record" object because there could be (and is)
        overlap of keys in this object and the "root" object.  

        Maybe this is the wrong decision? Post an issue, and let us know your 
        thoughts!

        Parse the response and return an iterator of result rows.
        """
        #Create a record object
        json = response.json()
        props: Dict = json.get(prop_key)
        ids: List = json.get(ids_key)
        for id in ids:
            record = {}
            prop_values: List = json[jobj_key][id]
            for property_name, property_index in props.items():
                record[property_name] = prop_values[property_index]
            return_object: Dict = copy.deepcopy(json)
            return_object[primary_key_name] = id
            return_object.pop(prop_key)
            return_object.pop(ids_key)
            return_object.pop(jobj_key)
            return_object["record"] = record
            yield return_object

        return {}
