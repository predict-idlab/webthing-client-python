
from webthing_client.observation import Observation
from webthing_client.client import WebthingClient


def callback(property_uri: str, observation: Observation) -> None:
    """Callback for observations.

    Args:
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
        observation (Observation): Observation on Property | '{"timestamp": "2023-01-01T12:00:00.000Z", "value": 100}'
    """
    print(f"<{property_uri}>: {observation}")

def subscribe_to_property(webthing_fqdn: str, property_uri: str):
    """Subscribe to Observations of a Property.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        property_uri (str): Property (relative) uri | 'things/example.thing/properties/example.property'
    """
    client = WebthingClient(webthing_fqdn)
    client.subscribe_resource(property_uri, callback)
