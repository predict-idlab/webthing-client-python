from datetime import datetime, timezone
from urllib import parse


def parse_iso_time_format(iso: str) -> datetime:
    """Parse valid in ISO 8601 format strings into timezone aware datetime objects.

    Args:
        iso (str): Timestamp string in ISO 8601 format.

    Returns:
        datetime: Datetime.
    """
    time = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if time.tzinfo is None:
        time = time.replace(tzinfo=timezone.utc)
    return time

def parse_ms_time_format(ms: float) -> datetime:
    """Parse milliseconds since epoch into timezone aware datetime objects.

    Args:
        ms (float): Milliseconds since UNIX epoch.

    Returns:
        datetime: Datetime.
    """
    return datetime.fromtimestamp(ms/1000, timezone.utc)

def to_iso_time_format(time: datetime) -> str:
    """Return ISO 8601 format timestamp string with Zulu ('Z') for UTC offsets.

    Args:
        time (datetime): Datetime.

    Returns:
        str: ISO 8601 timestamp.
    """
    return time.isoformat().replace("+00:00", "Z")

def datetime_utc_now() -> datetime:
    """Returns the current time as timezone aware datetime object with timezone UTC.

    Returns:
        datetime: Datetime.
    """
    return datetime.now(timezone.utc)

def get_relative_uri(uri: str) -> str:
    """Returns the relative URI (path) from given URI (may already be relative).

    Args:
        uri (str): URI string.

    Returns:
        str: Relative URI string.
    """
    return parse.urlparse(uri).path.strip('/')
