from datetime import datetime
import json
import textwrap
from typing import *

from webthing_client.client import WebthingClient
from webthing_client.model.action.operation.operation import Operation
from webthing_client.model.action.request import Request
from webthing_client.model.action.resolution import Resolution
from webthing_client.model.event.event import Event
from webthing_client.model.event.event_type import EventType
from webthing_client.model.event.feedback import Feedback
from webthing_client.model.event.feedback_schema import FeedbackSchema
from webthing_client.model.event.observation import Observation
from webthing_client.model.event.stimulus import Stimulus
from webthing_client.model.user.user import User


def create_simple_event_resolution(webthing_fqdn: str, user_iri: str, event_iri: str):
    """Create a simple Resolution for all unresolved requests on event.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        event_iri (str): The event IRI | 'http://test.invalid/event/1'
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    print(f"Getting requests for event <{event_iri}>")

    # First get all requests for event (we know the return type is event)
    event_requests: List[Request[Event, Operation]] = client.get_unresolved_requests_resource(event_iri)

    print(f"Found {len(event_requests)} events")
    
    # If no requests found return
    if len(event_requests) == 0:
        print(f"No Requests to resolve, returning")
        return

    # Print requests
    for i, request in enumerate(event_requests):
        # Get the user for the request
        user: User = client.get_user(request.user_iri)

        print(f"------------------- Request {i+1} -------------------")
        print(f"Request:")
        print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))
        print(f"User:")
        print(textwrap.indent(json.dumps(user.to_json_object(), indent=2), "  "))
        print("")

    # Ask what request to accept
    accepted_request_number = int(input("Enter Request number to accept or '0' for rejecting all requests:\n"))

    # Get accepted request iri or None if 0
    accepted_request_iri = None if accepted_request_number == 0 else event_requests[accepted_request_number-1].iri
    
    # Finally perform resolution
    resolution: Resolution = client.create_simple_resolution(event_requests, accepted_request_iri)

    print("Created Resolution:")
    print(textwrap.indent(json.dumps(resolution.to_json_object(), indent=2), "  "))
