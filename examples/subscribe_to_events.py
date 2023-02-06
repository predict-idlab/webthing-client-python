
from webthing.event import Event
from webthing.client import WebthingClient


def callback(event: Event) -> None:
    """Callback for Events.

    Args:
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
        event (Event): Event on Property | '{"timestamp": "2023-01-01T12:00:00.000Z", "value": <JSON-LD>}'
    """
    print(f"Event: {event}")

def subscribe_to_events(webthing_fqdn: str):
    """Subscribe to Events on webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingClient(webthing_fqdn)
    client.subscribe_events(callback)
