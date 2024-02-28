from argparse import Action
from datetime import datetime
import json
import textwrap
from typing import *

from webthing_client.client import WebthingClient
from webthing_client.model.action.operation.operation import UpdateEventTypeOperation
from webthing_client.model.action.request import Request
from webthing_client.model.event.event_type import EventType
from webthing_client.model.event.feedback import Feedback


def update_event_type(webthing_fqdn: str, user_iri: str, event_type_iri: str, new_name: Optional[str]=None, new_feedback: Optional[Feedback]=None) -> None:
    """Update EventType with (validated) options.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        event_type_iri (str): IRI of event | 'http://test.invalid/event-type/1'
        new_name (Optional[str]): New name. Defaults to None.
        new_feedback (Optional[Feedback]): New feedback. Defaults to None.
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    # Only send request when actually changed
    if (new_name is None and new_feedback is None):
        print("Nothing to update, returning")
        return

    # Get old eventType using view self
    # If known for sure that user has write permissions get_event_type may be used (slightly faster)
    old_event_type: EventType = client.get_event_type_user_view(client._user_iri, event_type_iri)

    # All properties should be provided to update request, any unchanged properties are taken from event
    if (new_name is None):
        new_name = old_event_type.name
    if (new_feedback is None):
        new_feedback = old_event_type.feedback

    # Update an Event request
    request: Request[EventType, UpdateEventTypeOperation] = client.update_event_type_request(event_type_iri, new_name, new_feedback)

    print(f"Update EventType Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))

    # Get the updated event type
    event_type: EventType = request.operation.update

    print(f"Updated EventType:")
    print(textwrap.indent(json.dumps(event_type.to_json_object(), indent=2), "  "))
