from datetime import datetime
import json
import textwrap
from typing import *

from webthing_client.client import WebthingClient
from webthing_client.model.action.operation.operation import CreateEventOperation, UpdateEventOperation, DeleteEventOperation
from webthing_client.model.action.request import Request
from webthing_client.model.event.event import Event
from webthing_client.model.event.event_type import EventType
from webthing_client.model.event.feedback import Feedback
from webthing_client.model.event.feedback_schema import FeedbackSchema
from webthing_client.model.event.observation import Observation
from webthing_client.model.event.stimulus import Stimulus


def create_simple_event(webthing_fqdn: str, user_iri: str, property_iri: str, from_: datetime, to: datetime, event_type_iri: str, feedback_object: Dict[str,Any]) -> None:
    """Create a simple event with single property/stimulus and feedback JSON object which will be validated.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        property_iri (str): Property iri | 'http://test.invalid/property/1'
        from_ (datetime): From timestamp
        to (datetime): To timestamp
        event_type_iri (str): IRI of event type | 'http://test.invalid/event-type/1'
        feedback_object: (Dict[str,Any]): A JSON object containing properties that match event Feedback Schema in event type. | {"test": "input"}
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    # Get the eventType and the event Feedback Schema
    event_type: EventType = client.get_event_type(event_type_iri)
    event_feedback_schema: FeedbackSchema = client.get_event_feedback_schema(event_type.event_feedback_iri)

    print(f"Got following JSON Schema for EventType <{event_type_iri}>:")
    print(textwrap.indent(json.dumps(event_feedback_schema.schema, indent=2), "  "))
    print(f"Got following feedback:")
    print(textwrap.indent(json.dumps(feedback_object, indent=2), "  "))

    # Check if the raw feedback matches the schema
    if (not event_feedback_schema.valid_feedback_object(feedback_object)):
        print("Feedback object is not valid on schema!")
        return
    
    # Create Feedback from FeedbackSchema and raw feedback
    event_feedback: Feedback = event_feedback_schema.feedback_from_feedback_object(feedback_object)
        
    # Create the stimuli that describes the property and time period linked to an event
    stimulus = Stimulus(property_iri, Observation(from_), Observation(to))

    # Finally create a new Event request
    # If the user has write permissions it will imediatly perform the action (but still return a request)
    request: Request[Event, CreateEventOperation] = client.create_event_request([stimulus], event_type_iri, event_feedback)

    print(f"Create Event Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))

    # We know the operation is a CreateEventOperation
    create_event_operation: CreateEventOperation = request.operation

    # Finally get the new event
    event: Event = create_event_operation.create

    print(f"Created Event:")
    print(textwrap.indent(json.dumps(event.to_json_object(), indent=2), "  "))


def create_event(webthing_fqdn: str, user_iri: str, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> None:
    """Create an event from given (validated) properties.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        stimuli (List[Stimulus]): List of stimuli.
        event_type_iri (str): The IRI EventType of the event.
        feedback (Feedback): The feedback matching the event Feedback Schema in event type.
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    # Create a new Event request
    request: Request[Event, CreateEventOperation] = client.create_event_request(stimuli, event_type_iri, feedback)

    print(f"Create Event Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))

    # Get the new event
    event: Event = request.operation.create

    print(f"Created Event:")
    print(textwrap.indent(json.dumps(event.to_json_object(), indent=2), "  "))


def update_event(webthing_fqdn: str, user_iri: str, event_iri: str, new_stimuli: Optional[List[Stimulus]]=None, new_event_type_iri: Optional[str]=None, new_feedback: Optional[Feedback]=None) -> None:
    """Update event with (validated) options.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        event_iri (str): IRI of event | 'http://test.invalid/event/1'
        new_stimuli (Optional[List[Stimulus]], optional): New stimuli. Defaults to None.
        new_event_type_iri (Optional[str], optional): New event type. Defaults to None.
        new_feedback_object (Optional[Dict[str,Any]], optional): New feedback. Defaults to None.
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    # Only send request when actually changed
    if (new_stimuli is None and new_event_type_iri is None and new_feedback is None):
        print("Nothing to update, returning")
        return

    # Get old event using view self
    # If known for sure that user has write permissions get_event may be used (slightly faster)
    old_event: Event = client.get_event_self_view(event_iri)

    # All properties should be provided to update request, any unchanged properties are taken from event
    if (new_stimuli is None):
        new_stimuli = old_event.stimuli
    if (new_event_type_iri is None):
        new_event_type_iri = old_event.event_type_iri
    if (new_feedback is None):
        new_feedback = old_event.feedback

    # Update an Event request
    request: Request[Event, UpdateEventOperation] = client.update_event_request(event_iri, new_stimuli, new_event_type_iri, new_feedback)

    print(f"Update Event Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))

    # Get the updated event
    event: Event = request.operation.update

    print(f"Updated Event:")
    print(textwrap.indent(json.dumps(event.to_json_object(), indent=2), "  "))


def delete_event(webthing_fqdn: str, user_iri: str, event_iri: str) -> None:
    """Delete Event.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        user_iri (str): The user performing the request | 'http://test.invalid/user/1'
        event_iri (str): IRI of event | 'http://test.invalid/event/1'
    """
    client = WebthingClient(webthing_fqdn, user_iri)

    # Delete an Event request
    request: Request[Event, DeleteEventOperation] = client.delete_event_request(event_iri)

    print(f"Delete Event Request:")
    print(textwrap.indent(json.dumps(request.to_json_object(), indent=2), "  "))
