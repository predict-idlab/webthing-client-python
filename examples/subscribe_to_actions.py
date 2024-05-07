from typing import Any, cast
import json
import textwrap

from webthing_client.client import WebthingClient
from webthing_client.model.action.action import Action
from webthing_client.model.action.operation.operation import CreateEventOperation, Operation
from webthing_client.model.event.event import Event


def callback(action: Action[Any,Operation]) -> None:
    """Callback for Actions.

    Args:
        action (Action): New Action.
    """
    print(f"New Action:")
    print(textwrap.indent(json.dumps(action.to_json_object(), indent=2), "  "))

    # Only do something when action on event
    if action.operation.is_resource_type(Event):
        event_action: Action[Event, Operation] = action
        print(f"Got Event Action for event <{event_action.operation.resource_iri}>!")

    # Only do something when create event action
    if action.operation.is_type(CreateEventOperation):
        create_event_action: Action[Event, CreateEventOperation] = cast(Action[Event, CreateEventOperation], action)
        print(f"Got CreateEvent Action for event:")
        print(textwrap.indent(json.dumps(create_event_action.operation.create.to_json_object(), indent=2), "  "))

def subscribe_to_actions(webthing_fqdn: str):
    """Subscribe to new Actions on webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingClient(webthing_fqdn, secure=False)
    client.subscribe_to_actions(callback)
