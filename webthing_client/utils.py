from datetime import datetime, timezone
import json
from urllib.parse import quote
from typing import *
from dateutil import parser
from rdflib import Graph


def parse_iso_time_format(iso: Optional[str]) -> datetime:
    """Parse valid in ISO 8601 format strings into timezone aware datetime objects.

    Args:
        iso (str): Timestamp string in ISO 8601 format.

    Returns:
        datetime: Datetime.
    """
    if iso is None:
        return None
    time = parser.isoparse(iso)
    if time.tzinfo is None:
        time = time.replace(tzinfo=timezone.utc)
    return time

def parse_ms_time_format(ms: Optional[float]) -> datetime:
    """Parse milliseconds since epoch into timezone aware datetime objects.

    Args:
        ms (float): Milliseconds since UNIX epoch.

    Returns:
        datetime: Datetime.
    """
    return datetime.fromtimestamp(ms/1000, timezone.utc) if ms is not None else None

def to_iso_time_format(time: Optional[datetime]) -> str:
    """Return ISO 8601 format timestamp string with Zulu ('Z') for UTC offsets.

    Args:
        time (datetime): Datetime

    Returns:
        str: ISO 8601 timestamp.
    """
    return time.isoformat().replace("+00:00", "Z") if time is not None else None

def datetime_utc_now() -> datetime:
    """Returns the current time as timezone aware datetime object with timezone UTC.

    Returns:
        datetime: Datetime.
    """
    return datetime.now(timezone.utc)

def encode_uri_component(uri_component: Optional[str]):
    return quote(uri_component, safe="!~*'()") if uri_component is not None else None

def jsonld_object_to_graph(jsonld_object: dict, graph: Graph=None) -> Graph:
    """
    Convert a json-ld object to Graph.
    """
    if graph is None:
        graph = Graph()
    # Is there a better way than to serialize and load?
    return graph.parse(format='json-ld', data=json.dumps(jsonld_object))
