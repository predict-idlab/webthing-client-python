
from webthing_client.client import WebthingClient
from webthing_client.model.webthing_observation import WebthingObservation


def callback(observation: WebthingObservation) -> None:
    """New observation callback.

    Args:
        observation (WebthingObservation): New WebthingObservation.
    """
    print(f"New Observation at {observation.timestamp}: {observation.value}")

def subscribe_to_property(webthing_fqdn: str, property_iri: str):
    """Subscribe to a property on webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        property_iri (str): Property IRI | 'http://test.invalid/property/1'
    """
    client = WebthingClient(webthing_fqdn)
    client.subscribe_to_property(callback)
