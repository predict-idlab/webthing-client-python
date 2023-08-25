from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Generic, TypeVar
from datetime import datetime, timezone
import json

from .utils import parse_iso_time_format, parse_ms_time_format


T = TypeVar('T', dict, list, str, int, float, None, bool)
class Observation(Generic[T]):
    """Basic Observation class."""

    def __init__(self, timestamp: datetime, value: T) -> None:
        """Basic Observation class.

        Args:
            timestamp (datetime): Time of Observation.
            value (T): Value of Observation, JSON serializable.
        """
        super().__init__()
        self._timestamp: datetime = timestamp
        self._value: T = value

    @classmethod
    def from_timestamp_value(cls, timestamp: datetime, value: T) -> Observation:
        """Create from timestamp and value.

        Args:
            timestamp (datetime): Timestamp.
            value (T): Value.

        Returns:
            Observation: New Observation.
        """
        return cls(timestamp, value)

    @classmethod
    def from_ms_value(cls, ms: float, value: T) -> Observation:
        """Create from milliseconds since epoch timestamp and value.

        Args:
            ms (float): Millisenconds since UNIX epoch.
            value (T): Value.

        Returns:
            Observation: New Observation.
        """
        timestamp = parse_ms_time_format(ms)
        return cls.from_timestamp_value(timestamp, value)

    @classmethod
    def from_iso_value(cls, iso: str, value: T) -> Observation:
        """Create from ISO 8601 timestamp and value.

        Args:
            iso (str): ISO 8601 timestamp.
            value (T): Value.

        Returns:
            Observation: New Observation.
        """
        timestamp = parse_iso_time_format(iso)
        return cls.from_timestamp_value(timestamp, value)

    @classmethod
    def from_json_observation(cls, observation: dict) -> Observation:
        """Create from JSON Observation dictionary.

        Args:
            observation (dict): JSON Observation as dictionary.

        Returns:
            Observation: New Observation.
        """
        return cls.from_iso_value(observation['timestamp'], observation['value'])

    @classmethod
    def from_json_observation_string(cls, json_str: str) -> Observation:
        """Create from JSON Observation string.

        Args:
            json_str (str): JSON Observation as string.

        Returns:
            Observation: New Observation.
        """
        return cls.from_json_observation(json.loads(json_str))

    def get_timestamp(self) -> datetime:
        """Get the timestamp of the Observation.

        Returns:
            datetime: Timestamp.
        """
        return self._timestamp

    def get_timestamp_ms(self) -> float:
        """Get the timestamp of the Observation as miliseconds since epoch.

        Returns:
            float: Timestamp as milliseconds since UNIX epoch.
        """
        return self._timestamp.timestamp()*1000

    def get_value(self) -> T:
        """Get the value of the Observation.

        Returns:
            T: Value.
        """
        return self._value

    def to_json(self) -> dict:
        """Get the JSON dictionary representation of the Obervation.

        Returns:
            dict: JSON dictionary representation.
        """
        return {'timestamp': self._timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), 'value': self._value}

    def __str__(self) -> str:
        """Returns JSON string representation.

        Returns:
            str: JSON string.
        """
        return json.dumps(self.to_json())
