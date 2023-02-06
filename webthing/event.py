from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Union, List
from datetime import datetime, timezone
import json
from textwrap import dedent
from string import Template
from uuid import uuid4

from .observation import Observation
from .semantic import SemanticModel
from .utils import parse_iso_time_format, parse_ms_time_format, get_relative_uri, to_iso_time_format


class Stimulus:
    """Stimulus class."""

    def __init__(self, property_uri: str, from_: datetime, to: datetime) -> None:
        """Stimulus class.

        Args:
            property_uri (str): The (relative) URI of the Property, will be made relative.
            from_ (datetime): Start of Stimulus.
            to (datetime): End of Stimulus.
        """
        # Property uri is converted to relative if not yet
        self._property_relative_uri = get_relative_uri(property_uri)
        self._from = from_
        self._to = to

    @classmethod
    def from_iso(cls, property_uri: str, from_iso: str, to_iso: str) -> Stimulus:
        """Create from ISO 8601 timestamps and Property URI.

        Args:
            property_uri (str): The (relative) URI of the Property, will be made relative.
            from_iso (str): Start of Stimulus in ISO 8601 format.
            to_iso (str): End of Stimulus in ISO 8601 format.

        Returns:
            _type_: New Stimulus.
        """
        return cls(property_uri, parse_iso_time_format(from_iso), parse_iso_time_format(to_iso))

    @classmethod
    def from_ms(cls, property_uri: str, from_ms: float, to_ms: float) -> Stimulus:
        """Create from milliseconds timestamps and Property URI.

        Args:
            property_uri (str): The (relative) URI of the Property, will be made relative.
            from_iso (str): Start of Stimulus in milliseconds since UNIX epoch.
            to_iso (str): End of Stimulus in milliseconds since UNIX epoch.

        Returns:
            _type_: New Stimulus.
        """
        return cls(property_uri, parse_ms_time_format(from_ms), parse_ms_time_format(to_ms))

    def get_relative_uri_property(self) -> str:
        """Get the relative URI fo the Property associated with Stimulus.

        Returns:
            str: Relative URI of Property.
        """
        return self._property_relative_uri

    def get_from(self) -> datetime:
        """Get the start of the Stimulus.

        Returns:
            datetime: Start of Stimulus.
        """
        return self._from

    def get_to(self) -> datetime:
        """Get the end of the Stimulus.

        Returns:
            datetime: End of Stimulus.
        """
        return self._to

    TEMPLATE = dedent("""
    {
        "http://IBCNServices.github.io/Folio-Ontology/Folio.owl#observedProperty": {
            "@id": "$PROPERTY_URI"
        },
        "http://IBCNServices.github.io/Folio-Ontology/Folio.owl#fromObservation": {
            "http://www.w3.org/ns/sosa/resultTime": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                "@value": "$FROM"
            }
        },
        "http://IBCNServices.github.io/Folio-Ontology/Folio.owl#toObservation": {
            "http://www.w3.org/ns/sosa/resultTime": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                "@value": "$TO"
            }
        }
    }
    """).strip(' \n')

    def to_jsonld(self) -> dict:
        """Generate the JSON-LD describing the Stimulus.

        Returns:
            dict: JSON-LD dictionary.
        """
        json_str = Template(self.TEMPLATE).substitute(
            {
                "PROPERTY_URI": self._property_relative_uri,
                "FROM": to_iso_time_format(self._from),
                "TO": to_iso_time_format(self._to)
            })
        return json.loads(json_str)

    def __str__(self) -> str:
        """Returns JSON-LD string representation.

        Returns:
            str: JSON-LD string.
        """
        return str(json.dumps(self.to_jsonld()))


class Event(Observation[Union[dict, list]]):
    """Event class."""

    def __init__(self, relative_uri: str, result_time: datetime, description: str, stimuli: List[Stimulus]) -> None:
        """Event class.

        Args:
            relative_uri (str): The relative URI of the Event e.g. 'events/11111111-2222-3333-4444-555555555555'.
                                Should be globally unique (strongly recommended to use UUIDv4) and start with 'events/'.
            result_time (datetime): The result time of the Event.
            description (str): The description of the Event.
            stimuli (List[Stimulus]): The stimuli of the Event.
        """
        self._relative_uri = relative_uri
        self._result_time = result_time
        self._description = description
        self._stimuli = stimuli
        super().__init__(result_time, self.to_jsonld())

    # Override Observation
    @classmethod
    def from_timestamp_value(cls, timestamp: datetime, value: Union[dict, list]) -> Union[Event, None]:
        """Create from Observation timestamp and JSON-LD value.

        Args:
            timestamp (datetime): The timestamp of the Observation.
            value (Union[dict, list]): The JSON-LD value of the Observation.

        Returns:
            Union[Event, None]: New Event or None if invalid.
        """
        event = cls.from_jsonld(value)
        # Check if timestamp is equal to resulttime
        if event != None and event._result_time == timestamp:
            return event
        else:
            return None      

    @classmethod
    def from_semantic_model(cls, model: SemanticModel) -> Union[Event, None]:
        """Create from given Semantic Model.

        Args:
            model (SemanticModel): Semantic Model describing an Event.

        Returns:
            Union[Event, None]: New Event or None if invalid.
        """
        query = dedent("""
            SELECT *
            WHERE {
                ?eventUri sosa:resultTime ?resultTime ;
                    dcterms:description ?description ;
                    ssn:wasOriginatedBy _:stimulus .
                    
                _:stimulus folio:observedProperty ?propertyUri ;
                    folio:fromObservation [ sosa:resultTime ?from ] ;
                    folio:toObservation [ sosa:resultTime ?to ] .
            }
        """).strip(' \n')
        results = model.list_query(query)
        if len(results) == 0:
            return None

        relative_uri = get_relative_uri(results[0]["eventUri"])
        result_time = parse_iso_time_format(results[0]["resultTime"])
        description = results[0]["description"]

        # Get stimuli
        stimuli: List[Stimulus] = []
        for result in results:
            stimuli.append(Stimulus.from_iso(get_relative_uri(result["propertyUri"]), result["from"], result["to"]))

        return cls(relative_uri, result_time, description, stimuli)

    @classmethod
    def from_jsonld_string(cls, jsonld_str: str) -> Union[Event, None]:
        """Create from JSON-LD string.

        Args:
            jsonld_str (str): JSON-LD string describing Event.

        Returns:
            Union[Event, None]: New Event or None if invalid.
        """
        # Use placeholder base because event is all relative (and otherwise uses local filepath)
        model = SemanticModel.from_jsonld_string(jsonld_str, "http://unused.base.invalid")
        return cls.from_semantic_model(model)

    @classmethod
    def from_jsonld(cls, jsonld: Union[dict, list]) -> Union[Event, None]:
        """Create from JSON-LD dictionary.

        Args:
            jsonld_str (Union[dict, list]): JSON-LD dictionary describing Event.

        Returns:
            Union[Event, None]: New Event or None if invalid.
        """
        # Convert object back to string (rdflib always expects strings)
        return cls.from_jsonld_string(json.dumps(jsonld))

    @classmethod
    def from_new_stimuli(cls, stimuli: List[Stimulus], description: str="Unknown Event", result_time: datetime=None, uri_suffix: str=None) -> Event:
        """Create a new Event from stimuli and parameters.

        Args:
            stimuli (List[Stimulus]): Stimuli associated with Event.
            description (str, optional): The description of the Event. Defaults to "Unknown Event".
            result_time (datetime, optional): The result time of the Event, None defaults to earliest start stimuli. Defaults to None.
            uri_suffix (str, optional): A string to append to relative uri e.g. 'events/11-22-33-44.<suffix>', use with caution. Defaults to None.

        Returns:
            Event: New Event.
        """
        relative_uri = f"events/{uuid4()}"
        if uri_suffix is not None:
            relative_uri = f"{relative_uri}.{uri_suffix}"
        if result_time is None:
            froms = [stimulus.get_from() for stimulus in stimuli]
            froms.sort()
            result_time = froms[0]
        return cls(relative_uri, result_time, description, stimuli)
        
    TEMPLATE = dedent("""
    {
        "@id": "$EVENT_URI",
        "http://purl.org/dc/terms/description": {
            "@type": "http://www.w3.org/2001/XMLSchema#string",
            "@value": "$DESCRIPTION"
        },
        "http://www.w3.org/ns/sosa/resultTime": {
            "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
            "@value": "$RESULT_TIME"
        },
        "http://www.w3.org/ns/ssn/wasOriginatedBy": null
    }
    """).strip(' \n')

    def to_jsonld(self) -> dict:
        """Generate the JSON-LD describing the Event.

        Returns:
            dict: JSON-LD dictionary.
        """
        stimuli_jsonld = [stimulus.to_jsonld() for stimulus in self._stimuli]
        if len(stimuli_jsonld) == 1:
            stimuli_jsonld = stimuli_jsonld[0]
        json_str = Template(self.TEMPLATE).substitute(
            {
                "EVENT_URI": self._relative_uri,
                "DESCRIPTION": self._description,
                "RESULT_TIME": to_iso_time_format(self._result_time)
            })
        event_jsonld = json.loads(json_str)
        event_jsonld["http://www.w3.org/ns/ssn/wasOriginatedBy"] = stimuli_jsonld
        return event_jsonld

    def get_relative_uri(self) -> str:
        """Get the relative URI of the Event.

        Returns:
            str: Relative URI.
        """
        return self._relative_uri

    def get_result_time(self) -> datetime:
        """Get the result time of the Event.

        Returns:
            datetime: Result time.
        """
        return self._result_time

    def get_description(self) -> str:
        """Get the description of the Event.

        Returns:
            str: Description.
        """
        return self._description

    def get_stimuli(self) -> List[Stimulus]:
        """Get the stimuli of the Event.

        Returns:
            List[Stimulus]: Stimuli.
        """
        return self._stimuli

    def get_uri_suffix(self) -> Union[str, None]:
        """Get the suffix of the relative URI.
        Use with caution, consider events from other sources also with suffix.

        Returns:
            Union[str, None]: The suffix if it exists, else None.
        """
        parts = self._relative_uri.split('.', 1)
        if len(parts) > 1:
            return parts[1]
        else:
            return None
