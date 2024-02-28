import json
import textwrap

from webthing_client.client import WebthingClient
from webthing_client.model.event.event import Event


def callback(event: Event) -> None:
    """Callback for Events.

    Args:
        event (Event): New Event.
    """
    print(f"New Event:")
    print(textwrap.indent(json.dumps(event.to_json_object(), indent=2), "  "))

def subscribe_to_events(webthing_fqdn: str):
    """Subscribe to new Events on webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingClient(webthing_fqdn)
    client.subscribe_to_events(callback)
