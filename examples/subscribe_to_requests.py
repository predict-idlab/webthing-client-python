from typing import Any, cast
import json
import textwrap

from webthing_client.client import WebthingClient
from webthing_client.model.action.operation.operation import CreateEventOperation, Operation
from webthing_client.model.action.request import Request
from webthing_client.model.event.event import Event


def callback(request: Request[Any, Operation]) -> None:
    """Callback for Requests.

    Args:
        request (Request): New Request.
    """
    print(f"New Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))

    # Only do something when request on event
    if request.operation.is_resource_type(Event):
        event_request: Request[Event, Operation] = request
        print(f"Got Event Request for event <{event_request.operation.resource_iri}>!")

    # Only do something when create event request
    if request.operation.is_type(CreateEventOperation):
        create_event_request: Request[Event, CreateEventOperation] = cast(Request[Event, CreateEventOperation], request)
        print(f"Got CreateEvent Request for event:")
        print(textwrap.indent(json.dumps(create_event_request.operation.create.to_json_object(), indent=2), "  "))

def subscribe_to_requests(webthing_fqdn: str):
    """Subscribe to new Requests on webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingClient(webthing_fqdn)
    client.subscribe_to_requests(callback)
