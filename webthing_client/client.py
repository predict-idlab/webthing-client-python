from datetime import datetime
import json
from typing import *
import requests

from .standard_api.api_handler import ApiRequester

from .input.iri_input import IRIInput
from .input.from_to_input import FromToInput
from .input.property_observations_input import PropertyObservationsInput
from .input.action.from_to_user_input import FromToUserInput
from .input.action.event_input import CreateEventInput, UpdateEventInput
from .input.action.event_type_input import UpdateEventTypeInput
from .input.action.iri_user_input import IRIUserInput
from .input.action.resolution_input import ResolutionInput
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

from .stomp import StompWebsocket
from .utils import encode_uri_component


class WebthingClient:
    """Client for interacting with a Webthing."""

    def __init__(self, webthing_fqdn: str, user_iri: Optional[str]=None, secure: bool=True, websocket: bool=True):
        """
        Client for interacting with a Webthing.

        Args:
            webthing_fqdn (str): The fully quallified domain name e.g. 'webthing.example.com'.
            user_iri (Optional[str]): The user IRI to use when performing actions if None will fail if performing actions.
            secure (bool, optional): If the Webthing uses TLS (https and wss). Defaults to True.
            websocket (bool, optional): If the websocket should be opened. Defaults to True.
                                        All websocket (subcribe) related functions will fail if set to False.
        """
        self._webthing_fqdn: str = webthing_fqdn.strip('/')
        self._secure: bool = secure
        self._user_iri: str = user_iri

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
        self._ws.subscribe(f'/properties/{encode_uri_component(property_iri)}',
            lambda message: callback(WebthingClient._process_observation(message)))

    def subscribe_to_events(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to realtime Events.

        Args:
            callback (Callable[[Event], None]): Callback for new Events.
        """
        self._ws.subscribe('/events', lambda json_str: callback(Event.from_json_object(json.loads(json_str))))

    def subscribe_to_actions(self, callback: Callable[[Action[Any,Operation]], None]) -> None:
        """Subscribe to realtime Actions.

        Args:
            callback (Callable[[Action[Any,Operation], None]): Callback for new Actions.
        """
        self._ws.subscribe('/actions', lambda json_str: callback(Action.from_json_object(json.loads(json_str))))

    def subscribe_to_requests(self, callback: Callable[[Request[Any,Operation]], None]) -> None:
        """Subscribe to realtime Requests.

        Args:
            callback (Callable[[Request[Any,Operation], None]): Callback for new Requests.
        """
        self._ws.subscribe('/requests', lambda json_str: callback(Request.from_json_object(json.loads(json_str))))

    def subscribe_to_resolutions(self, callback: Callable[[Resolution], None]) -> None:
        """Subscribe to realtime Resolutions.

        Args:
            callback (Callable[[Resolution], None]): Callback for new Resolutions.
        """
        self._ws.subscribe('/resolutions', lambda json_str: callback(Resolution.from_json_object(json.loads(json_str))))

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
    
    def get_event_self_view(self, event_iri: str) -> Event:
        """Get event with view as user set in client.

        Args:
            event_iri (str): The IRI
        Returns:
            Event: Event.
        """
        return self.get_event_user_view(self._user_iri)
    
    def get_events(self, from_: Optional[datetime]=None, to: Optional[datetime]=None) -> List[Event]:
        """Get all events in optional range.

        Args:
            from_ (Optional[datetime], optional): From time. Defaults to None.
            to (Optional[datetime], optional): To time. Defaults to None.

        Returns:
            List[Event]: Events in range.
        """
        json_array: Dict[str, Any] = self._api_requester.call('get_events',
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
        operation: Operation[Any] = None
        verdicts: Dict[str,VerdictResultType] = {}
        for request in requests:
            if request.iri == accapted_request_iri:
                operation = request.operation
                verdicts[request.iri] = VerdictResultType.ACCEPTED
            else:
                verdicts[request.iri] = VerdictResultType.REJECTED
        return self.create_resolution(verdicts, operation)
    
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
            PropertyObservationsInput.to_json_object(property_iri, from_time, to_time))
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
        response: requests.Response = requests.get(self._webthing_url + "/admin/delete_graph", params={'graph': encode_uri_component(graph_iri)})
        return response.text
    
    def replace_graph(self, graph: str, graph_iri: Optional[str]) -> None:
        """Replace the graph with graph IRI, if graph_iri is null then replace the default graph.

        Args:
            graph (str): The new graph in Turtle
            graph_iri (Optional[str]): The graph IRI
        """
        response: requests.Response = requests.post(self._webthing_url + "/admin/replace_graph",
                                                    headers={'Content-type': 'text/turtle'},
                                                    params={'graph': encode_uri_component(graph_iri)},
                                                    data=graph.encode('utf-8'))
        return response.text

    def reload(self) -> None:
        """Reload the webthing.
        """
        requests.Response = requests.get(self._webthing_url + "/admin/reload")
