from __future__ import annotations # Allow referencing enclosing class in typings
from typing import List, Dict, Optional, TypeVar, Callable, Any
from datetime import datetime
import json
import re
from rdflib import Graph
import requests

from .standard_api.api_handler import ApiRequester

from .input.iri_input import IRIInput
from .input.from_to_input import FromToInput
from .input.property.observations_input import ObservationsInput
from .input.property.properties_input import PropertiesInput
from .input.action.from_to_user_input import FromToUserInput
from .input.action.event_input import CreateEventInput, UpdateEventInput
from .input.action.event_type_input import UpdateEventTypeInput
from .input.action.iri_user_input import IRIUserInput
from .input.action.resolution_input import ResolutionInput
from .input.replay.replay_input import ReplayInput
from .model.webthing_observation import WebthingObservation
from .model.event.event import Event
from .model.event.stimulus import Stimulus
from .model.event.feedback import Feedback
from .model.event.feedback_schema import FeedbackSchema
from .model.event.event_type import EventType
from .model.action.action import Action
from .model.action.request import Request
from .model.action.operation.operation import Operation, CreateEventOperation, UpdateEventOperation, DeleteEventOperation, UpdateEventTypeOperation
from .model.action.resolution import Resolution, VerdictResultType
from .model.user.user import User
from .model.property.observable_property import ObservableProperty
from .model.system.sensor import Sensor
from .model.system.system import System
from .model.replay.replay import Replay

from .stomp import StompWebsocket
from .utils import encode_uri_component, jsonld_object_to_graph


class WebthingClient:
    """Client for interacting with a Webthing."""

    def __init__(self, webthing_fqdn: str, user_iri: Optional[str]=None, secure: bool=True, websocket: bool=True):
        """Client for interacting with a Webthing.

        Args:
            webthing_fqdn (str): The fully quallified domain name e.g. 'webthing.example.com'.
            user_iri (Optional[str]): The user IRI to use when performing actions if None will fail if performing actions.
            secure (bool, optional): If the Webthing uses TLS (https and wss). Defaults to True.
            websocket (bool, optional): If the websocket should be opened. Defaults to True.
                                        All websocket (subcribe) related functions will fail if set to False.
        """
        self._webthing_fqdn: str = webthing_fqdn.strip('/')
        self._secure: bool = secure
        self._user_iri: Optional[str] = user_iri

        if self._secure:
            self._ws_uri = f"wss://{self._webthing_fqdn}/websocket-stomp"
        else:
            self._ws_uri = f"ws://{self._webthing_fqdn}/websocket-stomp"
        
        if websocket:
            self._ws = StompWebsocket(self._ws_uri)
        else:
            self._ws = None

        if self._secure:
            self._webthing_url = f"https://{self._webthing_fqdn}"
        else:
            self._webthing_url = f"http://{self._webthing_fqdn}"

        self._api_requester = ApiRequester(self._webthing_url)

    @classmethod
    def url(cls, url: str, user_iri: Optional[str]=None, websocket: bool=True) -> WebthingClient:
        """Client for interacting with a Webthing from url.

        Args:
            url (str): The url of the webthing e.g. 'https://webthing.example.com'.
            user_iri (Optional[str]): The user IRI to use when performing actions if None will fail if performing actions.
            websocket (bool, optional): If the websocket should be opened. Defaults to True.
                                        All websocket (subcribe) related functions will fail if set to False.
        """
        # Determine if secure or not
        secure: bool = not url.startswith("http://")
        url_parser = re.compile(r"https?://")
        return WebthingClient(url_parser.sub('', url), user_iri=user_iri, secure=secure, websocket=websocket)

    PT = TypeVar('PT', dict, list, str, int, float, None, bool)
    @classmethod
    def _process_observation(cls, json_str: str) -> WebthingObservation[PT]:
        return WebthingObservation.from_json_object(json.loads(json_str))
    
    def subscribe_to_property(self, property_iri: str, callback: Callable[[WebthingObservation[PT]], None]) -> None:
        """Subscribe to realtime WebthingObservations for the given property.

        Args:
            property_iri (str): The IRI of the property.
            callback (Callable[[WebthingObservation[PT]], None]): Callback for new WebthingObservation.
        """
        assert self._ws is not None
        self._ws.subscribe(f'/properties/{encode_uri_component(property_iri)}',
            lambda message: callback(WebthingClient._process_observation(message)))

    def subscribe_to_events(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to realtime Events.

        Args:
            callback (Callable[[Event], None]): Callback for new Events.
        """
        assert self._ws is not None
        self._ws.subscribe('/events', lambda json_str: callback(Event.from_json_object(json.loads(json_str))))

    def subscribe_to_actions(self, callback: Callable[[Action[Any,Operation]], None]) -> None:
        """Subscribe to realtime Actions.

        Args:
            callback (Callable[[Action[Any,Operation], None]): Callback for new Actions.
        """
        assert self._ws is not None
        self._ws.subscribe('/actions', lambda json_str: callback(Action.from_json_object(json.loads(json_str))))

    def subscribe_to_requests(self, callback: Callable[[Request[Any,Operation]], None]) -> None:
        """Subscribe to realtime Requests.

        Args:
            callback (Callable[[Request[Any,Operation], None]): Callback for new Requests.
        """
        assert self._ws is not None
        self._ws.subscribe('/requests', lambda json_str: callback(Request.from_json_object(json.loads(json_str))))

    def subscribe_to_resolutions(self, callback: Callable[[Resolution], None]) -> None:
        """Subscribe to realtime Resolutions.

        Args:
            callback (Callable[[Resolution], None]): Callback for new Resolutions.
        """
        assert self._ws is not None
        self._ws.subscribe('/resolutions', lambda json_str: callback(Resolution.from_json_object(json.loads(json_str))))

    def get_property(self, property_iri: str) -> ObservableProperty:
        """Get ObservableProperty with IRI.

        Args:
            property_iri (str): IRI of property.

        Returns:
            ObservableProperty: ObservableProperty
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_property',
            IRIInput.to_json_object(property_iri))
        return ObservableProperty.from_json_object(json_object)
    
    def get_property_graph(self, property_iri: str, graph: Optional[Graph]=None) -> Graph:
        """Get ObservableProperty with IRI.

        Args:
            property_iri (str): IRI of property.
            graph (Optional[Graph]); The graph to insert to.

        Returns:
            Graph: ObservableProperty as Graph
        """
        jsonld: Dict[str, Any] = self._api_requester.call('get_property_jsonld',
            IRIInput.to_json_object(property_iri))
        return jsonld_object_to_graph(jsonld, graph)
    
    def get_properties(self, property_iris: Optional[List[str]]=None) -> List[ObservableProperty]:
        """Get all ObservableProperties or if property IRIs are provided those properties.

        Args:
            property_iris (Optional[List[str]]): The properties to retrieve. Defaults to None.

        Returns:
            List[ObservableProperty]: ObservableProperties
        """
        if (property_iris is not None and len(property_iris) == 0):
            return []
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_properties',
            PropertiesInput.to_json_object(property_iris))
        return [ObservableProperty.from_json_object(property_object) for property_object in json_array]
    
    def get_properties_count(self) -> int:
        """Get the count of properties, useful to check if processing all properties at once is too slow, filter on systems and sensors.

        Returns:
            int: The properties count.
        """
        count: int = self._api_requester.call('get_properties_count', {})
        return count
    
    def get_sensor(self, sensor_iri: str) -> Sensor:
        """Get Sensor with IRI.

        Args:
            sensor_iri (str): IRI of sensor.

        Returns:
            ObservableSensor: Sensor
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_sensor',
            IRIInput.to_json_object(sensor_iri))
        return Sensor.from_json_object(json_object)
    
    def get_sensors(self) -> List[Sensor]:
        """Get all Sensors.

        Returns:
            List[ObservableSensor]: Sensors
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_sensors', {})
        return [Sensor.from_json_object(sensor_object) for sensor_object in json_array]
    
    def get_system(self, system_iri: str) -> System:
        """Get System with IRI.

        Args:
            system_iri (str): IRI of system.

        Returns:
            ObservableSystem: System
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_system',
            IRIInput.to_json_object(system_iri))
        return System.from_json_object(json_object)
    
    def get_systems(self) -> List[System]:
        """Get all Systems.

        Returns:
            List[ObservableSystem]: Systems
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_systems', {})
        return [System.from_json_object(system_object) for system_object in json_array]

    def get_event(self, event_iri: str) -> Event:
        """Get event with IRI.

        Args:
            event_iri (str): IRI of event.

        Returns:
            Event: Event.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event',
            IRIInput.to_json_object(event_iri))
        return Event.from_json_object(json_object)
    
    def get_event_user_view(self, user_iri: str, event_iri: str) -> Event:
        """Get event with IRI as provided user.

        Args:
            user_iri (str): The IRI of the user.
            event_iri (str): The IRI
        Returns:
            Event: Event.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event_user_view',
            IRIUserInput.to_json_object(user_iri, event_iri))
        return Event.from_json_object(json_object)
    
    def get_event_graph(self, event_iri: str, graph: Optional[Graph]=None) -> Graph:
        """Get event with IRI.

        Args:
            event_iri (str): IRI of event.
            graph (Optional[Graph]); The graph to insert to.

        Returns:
            Graph: Event as Graph.
        """
        jsonld: Dict[str, Any] = self._api_requester.call('get_event_jsonld',
            IRIInput.to_json_object(event_iri))
        return jsonld_object_to_graph(jsonld, graph)
    
    def get_event_user_view_graph(self, user_iri: str, event_iri: str, graph: Optional[Graph]=None) -> Graph:
        """Get event with IRI as provided user.

        Args:
            user_iri (str): The IRI of the user.
            event_iri (str): IRI of event.
            graph (Optional[Graph]); The graph to insert to.

        Returns:
            Graph: Event as Graph.
        """
        jsonld: Dict[str, Any] = self._api_requester.call('get_event_user_view_jsonld',
            IRIUserInput.to_json_object(user_iri, event_iri))
        return jsonld_object_to_graph(jsonld, graph)
    
    def get_event_self_view(self, event_iri: str) -> Event:
        """Get event with view as user set in client.

        Args:
            event_iri (str): The IRI
        Returns:
            Event: Event.
        """
        assert self._user_iri is not None
        return self.get_event_user_view(self._user_iri, event_iri)
    
    def get_events(self, from_: Optional[datetime]=None, to: Optional[datetime]=None) -> List[Event]:
        """Get all events in optional range.

        Args:
            from_ (Optional[datetime], optional): From time. Defaults to None.
            to (Optional[datetime], optional): To time. Defaults to None.

        Returns:
            List[Event]: Events in range.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_events',
            FromToInput.to_json_object(from_, to))
        return [Event.from_json_object(event_object) for event_object in json_array]
    
    def get_events_user_view(self, user_iri: str, from_: Optional[datetime]=None, to: Optional[datetime]=None) -> List[Event]:
        """Get all events as user in optional range.

        Args:
            user_iri (str): User IRI.
            from_ (Optional[datetime], optional): From time. Defaults to None.
            to (Optional[datetime], optional): To time. Defaults to None.

        Returns:
            List[Event]: Events in range for user.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_events_user_view',
            FromToUserInput.to_json_object(user_iri, from_, to))
        return [Event.from_json_object(event_object) for event_object in json_array]
    
    def get_events_self_view(self, from_: Optional[datetime]=None, to: Optional[datetime]=None) -> List[Event]:
        """Get event with view as user set in client.

        Args:
            from_ (Optional[datetime], optional): From time. Defaults to None.
            to (Optional[datetime], optional): To time. Defaults to None.
        Returns:
            List[Event]: Events in range for self.
        """
        assert self._user_iri is not None
        return self.get_events_user_view(self._user_iri, from_, to)

    def create_event_request(self, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> Request[Event, CreateEventOperation]:
        """Perform a create event request, depending on the write status of the user in webthing this may also generate an action.

        Args:
            stimuli (List[Stimulus]): Stimuli of event.
            event_type_iri (str): Event type of event, should match feedback.
            feedback (Feedback): Feedback of event, should match event type.

        Returns:
            Request[Event, CreateEventOperation]: Resulting request.
        """
        assert self._user_iri is not None
        json_object: Dict[str, Any] = self._api_requester.call('create_event',
            CreateEventInput.to_json_object(self._user_iri, stimuli, event_type_iri, feedback))
        return Request.from_json_object(json_object)
    
    def update_event_request(self, event_iri: str, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> Request[Event, UpdateEventOperation]:
        """Perform an update event request, depending on the write status of the user in webthing this may also generate an action.

        Args:
            event_iri: (str): IRI of Event.
            stimuli (List[Stimulus]): Stimuli of event.
            event_type_iri (str): Event type of event, should match feedback.
            feedback (Feedback): Feedback of event, should match event type.

        Returns:
            Request[Event, UpdateEventOperation]: Resulting request.
        """
        assert self._user_iri is not None
        json_object: Dict[str, Any] = self._api_requester.call('update_event',
            UpdateEventInput.to_json_object(self._user_iri, event_iri, stimuli, event_type_iri, feedback))
        return Request.from_json_object(json_object)
    
    def delete_event_request(self, event_iri: str) -> Request[Event, DeleteEventOperation]:
        """Perform a delete event request, depending on the write status of the user in webthing this may also generate an action.

        Args:
            event_iri: (str): IRI of Event.

        Returns:
            Request[Event, DeleteEventOperation]: Resulting request.
        """
        assert self._user_iri is not None
        json_object: Dict[str, Any] = self._api_requester.call('delete_event',
            IRIUserInput.to_json_object(self._user_iri, event_iri))
        return Request.from_json_object(json_object)
    
    def get_event_type(self, event_type_iri: str) -> EventType:
        """Get Event Type with IRI.

        Args:
            event_type_iri (str): IRI of Event Type.

        Returns:
            EventType: Event Type.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event_type',
            IRIInput.to_json_object(event_type_iri))
        return EventType.from_json_object(json_object)
    
    def get_event_type_user_view(self, user_iri: str, event_type_iri: str) -> EventType:
        """Get Event Type with IRI viewed as user.

        Args:
            user_iri (str): IRI of user.
            event_type_iri (str): IRI of Event Type.

        Returns:
            EventType: Event Type view.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event_type_user_view',
            IRIUserInput.to_json_object(user_iri, event_type_iri))
        return EventType.from_json_object(json_object)
    
    def get_event_type_self_view(self, event_type_iri: str) -> EventType:
        """Get Event Type with view self.

        Args:
            event_type_iri (str): IRI of Event Type.

        Returns:
            EventType: Event Type view.
        """
        assert self._user_iri is not None
        return self.get_event_type_user_view(self._user_iri, event_type_iri)
    
    def get_event_types(self) -> List[EventType]:
        """Get all known Event Types.

        Returns:
            List[EventType]: List of Event Types.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_event_types')
        return [EventType.from_json_object(event_type_object) for event_type_object in json_array]

    def update_event_type_request(self, event_type_iri: str, name: str, feedback: Feedback) -> Request[EventType, UpdateEventTypeOperation]:
        """Perform an update event type request, depending on the write status of the user in webthing this may also generate an action.

        Args:
            event_type_iri: (str): IRI of Event Type.
            name (str): Name of Event Type.
            feedback (Feedback): Feedback of Event Type.

        Returns:
            Request[EventType, UpdateEventTypeOperation]: Resulting request.
        """
        assert self._user_iri is not None
        json_object: Dict[str, Any] = self._api_requester.call('update_event_type',
            UpdateEventTypeInput.to_json_object(self._user_iri, event_type_iri, name, feedback))
        return Request.from_json_object(json_object)

    def get_event_feedback_schema(self, event_feedback_iri: str) -> FeedbackSchema:
        """Get the feedback schema from the event feedback IRI.

        Args:
            event_feedback_iri (str): The event feedback iri in Event Type.

        Returns:
            FeedbackSchema: The schema.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event_feedback_schema',
            IRIInput.to_json_object(event_feedback_iri))
        return FeedbackSchema.from_json_object(json_object)

    def get_event_type_feedback_schema(self, type_feedback_iri: str) -> FeedbackSchema:
        """Get the feedback schema from the type feedback IRI.

        Args:
            type_feedback_iri (str): The type feedback iri in Event Type.

        Returns:
            FeedbackSchema: The schema.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_event_type_feedback_schema',
            IRIInput.to_json_object(type_feedback_iri))
        return FeedbackSchema.from_json_object(json_object)
    
    def get_request(self, request_iri: str) -> Request:
        """Get the Request by IRI.

        Args:
            request_iri (str): Request IRI.

        Returns:
            Request: The Request.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_request',
            IRIInput.to_json_object(request_iri))
        return Request.from_json_object(json_object)
    
    def get_requests(self) -> List[Request[Any, Operation]]:
        """Get all requests.

        Returns:
            List[Request[Any, Operation]]: All requests.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_requests')
        return [Request.from_json_object(request_object) for request_object in json_array]

    def get_requests_resource(self, resource_iri: str) -> List[Request[Any, Operation]]:
        """Get all requests linked to resource IRI.

        Args:
            resource_iri (str): The IRI of the resource.

        Returns:
            List[Request[Any, Operation]]: All linked requests.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_requests_resource',
            IRIInput.to_json_object(resource_iri))
        return [Request.from_json_object(request_object) for request_object in json_array]
    
    def get_unresolved_requests(self) -> List[Request[Any, Operation]]:
        """Get all unresolved requests.

        Returns:
            List[Request[Any, Operation]]: All unresolved requests.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_unresolved_requests')
        return [Request.from_json_object(request_object) for request_object in json_array]
    
    def get_unresolved_requests_resource(self, resource_iri: str) -> List[Request[Any, Operation]]:
        """Get all unresolved requests linked to resource IRI.

        Args:
            resource_iri (str): The IRI of the resource.

        Returns:
            List[Request[Any, Operation]]: All linked unresolved requests.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_unresolved_requests_resource',
            IRIInput.to_json_object(resource_iri))
        return [Request.from_json_object(request_object) for request_object in json_array]
    
    def get_action(self, action_iri: str) -> Action:
        """Get the Action by IRI.

        Args:
            action_iri (str): Action IRI.

        Returns:
            Action: The Action.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_action',
            IRIInput.to_json_object(action_iri))
        return Action.from_json_object(json_object)

    def get_actions(self) -> List[Action]:
        """Get all actions.

        Returns:
            List[Action]: All actions.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_actions')
        return [Action.from_json_object(action_object) for action_object in json_array]
    
    def get_actions_resource(self, resource_iri: str) -> List[Action]:
        """Get all actions linked to resource IRI.

        Args:
            resource_iri (str): The IRI of the resource.

        Returns:
            List[Action]: All linked actions.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_actions_resource',
            IRIInput.to_json_object(resource_iri))
        return [Action.from_json_object(action_object) for action_object in json_array]
    
    def get_resolution(self, resolution_iri: str) -> Resolution:
        """Get the Resolution by IRI.

        Args:
            resolution_iri (str): Resolution IRI.

        Returns:
            Resolution: The Resolution.
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_resolution',
            IRIInput.to_json_object(resolution_iri))
        return Resolution.from_json_object(json_object)
    
    def get_resolutions(self) -> List[Resolution]:
        """Get all resolutions.

        Returns:
            List[Resolution]: All resolutions.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_resolutions')
        return [Resolution.from_json_object(resolution_object) for resolution_object in json_array]

    def get_resolutions_resource(self, resource_iri: str) -> List[Resolution]:
        """Get all resolutions linked to resource IRI.

        Args:
            resource_iri (str): The IRI of the resource.

        Returns:
            List[Resolution]: All linked resolutions.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_resolutions_resource',
            IRIInput.to_json_object(resource_iri))
        return [Resolution.from_json_object(resolution_object) for resolution_object in json_array]

    def create_resolution(self, verdicts: Dict[str,VerdictResultType], operation: Optional[Operation[Any]]=None) -> Resolution:
        """Create a resolution based on input, user must have write permissions on webthing.

        Args:
            verdicts (Dict[str,VerdictResultType]): Dict of verdicts where key is request IRI and value the verdict result.
            operation (Optional[Operation[Any]], optional): _description_. The actual operation to perform.

        Returns:
            Resolution: The completed resolution.
        """
        assert self._user_iri is not None
        json_object: Dict[str, Any] = self._api_requester.call('create_resolution',
            ResolutionInput.to_json_object(self._user_iri, verdicts, operation))
        return Resolution.from_json_object(json_object)
    
    def create_simple_resolution(self, requests: List[Request[Any, Operation]], accapted_request_iri: Optional[str]=None) -> Resolution:
        """Create a Resolution where one or none of the requests are accepted.
        If there is an accpeted request the operation of the result will be the operation of the request.

        Args:
            requests (List[Request[Any, Operation]]): List of requests
            accapted_request_iri (Optional[str], optional): The accepted request. Defaults to None.

        Returns:
            Resolution: The completed resolution.
        """
        operation: Optional[Operation[Any]] = None
        verdicts: Dict[str,VerdictResultType] = {}
        for request in requests:
            if request.iri == accapted_request_iri:
                operation = request.operation
                verdicts[request.iri] = VerdictResultType.ACCEPTED
            else:
                verdicts[request.iri] = VerdictResultType.REJECTED
        return self.create_resolution(verdicts, operation)
    
    def get_users(self) -> List[User]:
        """Get all the users.

        Returns:
            List[User]: Users
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_user', {})
        return [User.from_json_object(user_object) for user_object in json_array]
    
    def get_user(self, user_iri: str) -> User:
        """Get the User associated with the IRI.

        Args:
            user_iri (str): User IRI

        Returns:
            User: The User
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_user',
            IRIInput.to_json_object(user_iri))
        return User.from_json_object(json_object)
    
    def get_self(self) -> User:
        """Get the User associated with User IRI in webthing.

        Returns:
            User: The User
        """
        assert self._user_iri is not None
        return self.get_user(self._user_iri)
    
    def get_observations(self, property_iri: str, from_time: Optional[datetime]=None, to_time: Optional[datetime]=None) -> List[WebthingObservation[PT]]:
        """Get observations for property. 

        Args:
            property_iri (str): The IRI of the property.
            from_time (Optional[datetime], optional): The start date. Defaults to None.
            to_time (Optional[datetime], optional): The end date. Defaults to None.

        Returns:
            List[WebthingObservation[PT]]: The observations.
        """
        json_array: List[Dict[str, Any]] = self._api_requester.call('get_property_observations',
            ObservationsInput.to_json_object(property_iri, from_time, to_time))
        return [WebthingObservation.from_json_object(observation_object) for observation_object in json_array]
    
    def get_last_observation(self, property_iri: str) -> Optional[WebthingObservation]:
        """Get the last Observation for the property IRI.

        Args:
            property_iri (str): Property IRI

        Returns:
            Optional[WebthingObservation]: Observation or None
        """
        json_object: Dict[str, Any] = self._api_requester.call('get_property_last_observation',
            IRIInput.to_json_object(property_iri))
        return WebthingObservation.from_json_object(json_object)


class WebthingAdminClient:
    """Class for admin endpoints on webthing."""

    def __init__(self, webthing_fqdn: str, secure: bool=True):
        """Client for admin endpoints.

        Args:
            webthing_fqdn (str): The fully quallified domain name e.g. 'webthing.example.com'.
            secure (bool, optional):  If the Webthing uses TLS (https). Defaults to True.
        """
        self._webthing_fqdn: str = webthing_fqdn.strip('/')
        self._secure: bool = secure

        if self._secure:
            self._webthing_url = f"https://{self._webthing_fqdn}"
        else:
            self._webthing_url = f"http://{self._webthing_fqdn}"

    @classmethod
    def url(cls, url: str) -> WebthingAdminClient:
        """Client for admin endpoints from url.

        Args:
            url (str): The url of the webthing e.g. 'https://webthing.example.com'.
        """
        # Determine if secure or not
        secure: bool = not url.startswith("http://")
        url_parser = re.compile(r"https?://")
        return WebthingAdminClient(url_parser.sub('', url), secure=secure)

    def get_graph(self, graph_iri: Optional[str]) -> str:
        """Get the graph with graph IRI, if graph_iri is null then get the default graph.

        Args:
            graph_iri (Optional[str]): The graph IRI

        Returns:
            str: The graph as Turtle.
        """
        response: requests.Response = requests.get(self._webthing_url + "/admin/get_graph", params={'graph': encode_uri_component(graph_iri)})
        return response.text

    def delete_graph(self, graph_iri: Optional[str]) -> None:
        """Delete the graph with graph IRI, if graph_iri is null then delete the default graph.

        Args:
            graph_iri (Optional[str]): The graph IRI
        """
        requests.get(self._webthing_url + "/admin/delete_graph", params={'graph': encode_uri_component(graph_iri)})
    
    def replace_graph(self, graph: str, graph_iri: Optional[str]) -> None:
        """Replace the graph with graph IRI, if graph_iri is null then replace the default graph.

        Args:
            graph (str): The new graph in Turtle
            graph_iri (Optional[str]): The graph IRI
        """
        requests.post(self._webthing_url + "/admin/replace_graph",
                    headers={'Content-type': 'text/turtle'},
                    params={'graph': encode_uri_component(graph_iri)},
                    data=graph.encode('utf-8'))

    def reload(self) -> None:
        """Reload the webthing.
        """
        requests.Response = requests.get(self._webthing_url + "/admin/reload")


class WebthingReplayClient:
    """Class for replay endpoints on webthing."""

    def __init__(self, webthing_fqdn: str, secure: bool=True):
        """Client for replay endpoints.

        Args:
            webthing_fqdn (str): The fully quallified domain name e.g. 'webthing.example.com'.
            secure (bool, optional):  If the Webthing uses TLS (https). Defaults to True.
        """
        self._webthing_fqdn: str = webthing_fqdn.strip('/')
        self._secure: bool = secure

        if self._secure:
            self._webthing_url = f"https://{self._webthing_fqdn}"
        else:
            self._webthing_url = f"http://{self._webthing_fqdn}"

        self._api_requester = ApiRequester(self._webthing_url)

    @classmethod
    def url(cls, url: str) -> WebthingAdminClient:
        """Client for replay endpoints from url.

        Args:
            url (str): The url of the webthing e.g. 'https://webthing.example.com'.
        """
        # Determine if secure or not
        secure: bool = not url.startswith("http://")
        url_parser = re.compile(r"https?://")
        return WebthingAdminClient(url_parser.sub('', url), secure=secure)

    def set_replay(self, from_historical: datetime,
                         to_historical: datetime,
                         from_replay: Optional[datetime] = None,
                         speed_multiplier: Optional[float] = None,
                         loop: Optional[bool] = None,
                         scale_timestamps: Optional[bool] = None,
                         seconds_interval: Optional[int] = None,
                         replay_semantic_submissions_user_iris: Optional[List[str]] = None) -> Replay:
        """Set the paramaters for replay.

        Args:
            from_historical (datetime): The historical window from.
            to_historical (datetime): The historical window to.
            from_replay (datetime): The current replay window from. Defaults to now.
            speed_multiplier (Optional[float], optional): The approximate multiplier to speed up or slow down. Defaults to 1.
            loop (Optional[bool], optional): Indicating if the replay is finished it should restart. Defaults to False.
            scale_timestamps (Optional[bool], optional): If the transformed historical timestamps should be scaled depending on speed, if true will change the difference between timestamps,
                if false will just move timestamps in time by the difference between historical and replay windows. Defaults to True.
            seconds_interval (Optional[int], optional): The polling interval to use. Defaults to 5 seconds.
            replay_semantic_submissions_user_iris (Optional[List[str]], optional): The IRI's of the users whose semantic submissions (requests,actions,resolutions) we must replay. Defaults to no users.

        Returns:
            Replay: The replay status.
        """
        json_object: Dict[str, Any] = self._api_requester.call('replay/set',
            ReplayInput.to_json_object(from_historical, to_historical, from_replay, speed_multiplier,
                                       loop, scale_timestamps, seconds_interval, replay_semantic_submissions_user_iris))
        return Replay.from_json_object(json_object)

    def start_replay(self) -> Replay:
        """Start the replay form set parameters.

        Returns:
            Replay: The replay status.
        """
        json_object: Dict[str, Any] = self._api_requester.call('replay/start', {})
        return Replay.from_json_object(json_object)
    
    def stop_replay(self) -> Replay:
        """Stop the replay.

        Returns:
            Replay: The replay status.
        """
        json_object: Dict[str, Any] = self._api_requester.call('replay/stop', {})
        return Replay.from_json_object(json_object)
