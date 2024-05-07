from datetime import datetime, timezone
import json
from urllib.parse import quote
from typing import Optional, overload
from dateutil import parser
from rdflib import Graph


@overload
def parse_iso_time_format(iso: str) -> datetime: ...
@overload
def parse_iso_time_format(iso: None) -> None: ...
def parse_iso_time_format(iso: Optional[str]) -> Optional[datetime]:
    """Parse valid in ISO 8601 format strings into timezone aware datetime objects.

    Args:
        iso (Optional[str]): Timestamp string in ISO 8601 format.

    Returns:
        Optional[datetime]: Datetime.
    """
    if iso is None:
        return None
    time = parser.isoparse(iso)
    if time.tzinfo is None:
        time = time.replace(tzinfo=timezone.utc)
    return time

@overload
def parse_ms_time_format(ms: float) -> datetime: ...
@overload
def parse_ms_time_format(ms: None) -> None: ...
def parse_ms_time_format(ms: Optional[float]) -> Optional[datetime]:
    """Parse milliseconds since epoch into timezone aware datetime objects.

    Args:
        ms (Optional[float]): Milliseconds since UNIX epoch.

    Returns:
        Optional[datetime]: Datetime.
    """
    return datetime.fromtimestamp(ms/1000, timezone.utc) if ms is not None else None

@overload
def to_iso_time_format(time: datetime) -> str: ...
@overload
def to_iso_time_format(time: None) -> None: ...
def to_iso_time_format(time: Optional[datetime]) -> Optional[str]:
    """Return ISO 8601 format timestamp string with Zulu ('Z') for UTC offsets.

    Args:
        time (Optional[datetime]): Datetime

    Returns:
        Optional[str]: ISO 8601 timestamp.
    """
    return time.isoformat().replace("+00:00", "Z") if time is not None else None

def datetime_utc_now() -> datetime:
    """Returns the current time as timezone aware datetime object with timezone UTC.

    Returns:
        datetime: Datetime.
    """
    return datetime.now(timezone.utc)

@overload
def encode_uri_component(uri_component: str) -> str: ...
@overload
def encode_uri_component(uri_component: None) -> None: ...
def encode_uri_component(uri_component: Optional[str]) -> Optional[str]:
    """Encode string as URI component (RFC3986)

    Args:
        uri_component (Optional[str]): The string to encode.

    Returns:
        Optional[str]: The encoded string.
    """
    return quote(uri_component, safe="!~*'()") if uri_component is not None else None

def jsonld_object_to_graph(jsonld_object: dict, graph: Optional[Graph]=None) -> Graph:
    """Convert the json-ld object to RDFLib Graph.

    Args:
        jsonld_object (dict): The json-ld object.
        graph (Optional[Graph], optional): The optional Graph to insert the object in. Defaults to None.

    Returns:
        Graph: Graph with the json-ld object.
    """
    if graph is None:
        graph = Graph()
    # Is there a better way than to serialize and load?
    return graph.parse(format='json-ld', data=json.dumps(jsonld_object))
