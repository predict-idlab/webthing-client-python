from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Union
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import json

from .observation import Observation
from .event import Event


class ActionType(Enum):
    CreateEvent = "create_event"
    UpdateEvent = "update_event"
    DeleteEvent = "delete_event"

class Action(ABC, Observation[dict]):
    """Base Action object."""

    @classmethod
    @property
    @abstractmethod
    def TYPE(cls) -> ActionType:
        """The ActionType of the Action class"""
        pass

    # Override Observation
    @classmethod
    def from_timestamp_value(cls, timestamp: datetime, value: dict) -> Union[Action, None]:
        """Create the correct Action class for the given JSON string.

        Args:
            timestamp (datetime): The timestamp of the Action Observation.
            value (dict): The value of the Action Observation as JSON dict.

        Returns:
            Union[Action, None]: Returns Action or None if invalid.
        """
        # Check key available
        type_keys = value.keys()
        if len(type_keys) != 1:
            return None

        type_str = list(type_keys)[0]
        try:
            action_type = ActionType(type_str)
        except ValueError:
            return None

        ACTION_TYPE_CLASS_MAPPING = {
            ActionType.CreateEvent: CreateEventAction,
            ActionType.UpdateEvent: UpdateEventAction,
            ActionType.DeleteEvent: DeleteEventAction
        }

        action_cls: Action = ACTION_TYPE_CLASS_MAPPING[action_type]
        return action_cls.from_timestamp_input_object(timestamp, value[type_str]["input"])

    @classmethod
    @abstractmethod
    def from_timestamp_input_object(cls, timestamp: datetime, input: dict) -> Union[Action, None]:
        """Create the Action class from the timestamp and the specific Action class input dict.

        Args:
            timestamp (datetime): The timestamp of the Action.
            input (dict): The specific dictionary of inputs for the Action class.

        Returns:
            Union[Action, None]: Action class or None if invalid.
        """
        pass

    def _value_from_inputs(self, inputs: dict) -> dict:
        return {self.TYPE.value: {"input": inputs}}

    def hash(self) -> int:
        """Get the operation hash from Action, this does not take into account the timestamp.

        Returns:
            int: Hash.
        """
        return hash(json.dumps(self._value))


class CreateEventAction(Action):
    """Create Event Action class."""

    TYPE = ActionType.CreateEvent

    def __init__(self, timestamp: datetime, event: Event, stream: bool) -> None:
        """Create Event Action class.

        Args:
            timestamp (datetime): Timestamp of Action.
            event (Event): The new Event associated with Action.
            stream (bool): If the Event was streamed.
        """
        self._event = event
        self._stream = stream
        super().__init__(timestamp, self._value_from_inputs({"id": self._event.get_relative_uri(), "stream": self._stream, "value": self._event.to_jsonld()}))

    # Override Action
    @classmethod
    def from_timestamp_input_object(cls, timestamp: datetime, input: dict) -> Union[CreateEventAction, None]:
        if not input.keys() & {"id", "stream", "value"}:
            return None
        # Value contains jsonld event
        event = Event.from_jsonld(input["value"])
        if event is None or event.get_relative_uri() != input["id"]:
            return None
        return cls(timestamp, event, input["stream"])

    def get_event(self) -> Event:
        """Get the Event associated with the Action.

        Returns:
            Event: Event.
        """
        return self._event
    
    def get_stream(self) -> bool:
        """Get if the event was streamed upon creation.

        Returns:
            bool: True if it was streamed.
        """
        return self._stream


class UpdateEventAction(Action):
    """Update Event Action class."""

    TYPE = ActionType.UpdateEvent

    def __init__(self, timestamp: datetime, event: Event) -> None:
        """Update Event Action class.

        Args:
            timestamp (datetime): Timestamp of Action.
            event (Event): The updated Event associated with Action.
        """
        self._event = event
        super().__init__(timestamp, self._value_from_inputs({"id": self._event.get_relative_uri(), "value": self._event.to_jsonld()}))

    # Override Action
    @classmethod
    def from_timestamp_input_object(cls, timestamp: datetime, input: dict) -> Union[UpdateEventAction, None]:
        if not input.keys() & {"id", "value"}:
            return None
        # Value contains jsonld event
        event = Event.from_jsonld(input["value"])
        if event is None or event.get_relative_uri() != input["id"]:
            return None
        return cls(timestamp, event)

    def get_event(self) -> Event:
        """Get the Event associated with the Action.

        Returns:
            Event: Event.
        """
        return self._event


class DeleteEventAction(Action):
    """Delete Event Action class."""

    TYPE = ActionType.DeleteEvent

    def __init__(self, timestamp: datetime, relative_uri: str) -> None:
        """Delete Event Action class.

        Args:
            timestamp (datetime): Timestamp of Action.
            event (Event): The Event relative URI associated with Action.
        """
        self._relative_uri = relative_uri
        super().__init__(timestamp, self._value_from_inputs({"id": self._relative_uri}))

    # Override Action
    @classmethod
    def from_timestamp_input_object(cls, timestamp: datetime, input: dict) -> Union[DeleteEventAction, None]:
        if "id" not in input:
            return None
        return cls(timestamp, input["id"])

    def get_relative_uri(self) -> str:
        """Ge the relative URI of the Event associated with the Action.

        Returns:
            str: Relative URI of Event.
        """
        return self._relative_uri
