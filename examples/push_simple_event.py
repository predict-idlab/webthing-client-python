from datetime import datetime

from webthing.event import Event, Stimulus
from webthing.client import WebthingClient


def push_simple_event(webthing_fqdn: str, property_uri: str, from_: str, to: str, description: str):
    """Push a simple event.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
        from_ (str): From ISO 8601 timestamp | '2023-01-01T12:00:00.000Z'
        to (str): To ISO 8601 timestamp | '2023-01-01T13:00:00.000Z'
        description (str): Event description | 'Example Description'
    """
    client = WebthingClient(webthing_fqdn)
    # The stimuli describe the property and time period linked to an event
    stimulus = Stimulus.from_iso(property_uri, from_, to)
    event = Event.from_new_stimuli(
        [stimulus],
        description=description
    )
    client.send_create_event_action(event)

def push_simple_event_ms(webthing_fqdn: str, property_uri: str, from_: float, to: float, description: str):
    """Push a simple event.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
        from_ (float): From in ms since epoch | '1672574400000'
        to (float): To in ms since epoch | '1672578000000'
        description (str): Event description | 'Example Description'
    """
    client = WebthingClient(webthing_fqdn)
    # The stimuli describe the property and time period linked to an event
    stimulus = Stimulus.from_ms(property_uri, from_, to)
    event = Event.from_new_stimuli(
        [stimulus],
        description=description
    )
    client.send_create_event_action(event)

def push_simple_event_datetime(webthing_fqdn: str, property_uri: str, from_: datetime, to: datetime, description: str):
    """Push a simple event.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
        from_ (datetime): From in python timezoneaware datetime | 'datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)'
        to (datetime): To in python timezoneaware datetime | 'datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)'
        description (str): Event description | 'Example Description'
    """
    client = WebthingClient(webthing_fqdn)
    # The stimuli describe the property and time period linked to an event
    stimulus = Stimulus(property_uri, from_, to)
    event = Event.from_new_stimuli(
        [stimulus],
        description=description
    )
    resp = client.send_create_event_action(event)
    if not resp.ok:
        print(resp.text)
