"""REST client handling, including ZohoSprintsStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.authenticators import (
    OAuthAuthenticator,
)
from singer_sdk.streams import RESTStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ZohoSprintsAuthenticator(OAuthAuthenticator):
    @property
    def oauth_request_body(self) -> dict:
        return {
            "grant_type": "refresh_token",
            "redirect_uri": "http://localhost",  # not needed, but api requires it
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
        }


class ZohoSprintsStream(RESTStream):
    """ZohoSprints stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    records_jsonpath = "$"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.next_index"  # Or override `get_next_page_token`.

    @property
    @cached
    def authenticator(self) -> ZohoSprintsAuthenticator:
        """Return a new authenticator object."""
        return ZohoSprintsAuthenticator(
            stream=self, auth_endpoint=self.config["oauth_url"]
        )

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
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # TODO: Delete this method if not needed.
        return row
