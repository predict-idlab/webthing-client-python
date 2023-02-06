from typing import Callable, Dict, List, Tuple, Set
import requests

from .utils import get_relative_uri, datetime_utc_now
from .stomp import StompWebsocket
from .observation import Observation
from .event import Event
from .action import ActionType, Action, CreateEventAction, UpdateEventAction, DeleteEventAction


class WebthingClient:
    """Client for interacting with a Webthing."""

    _EVENTS_URI = "events"
    _ACTIONS_URI = "actions"

    def __init__(self, webthing_fqdn: str, secure: bool = True):
        """Client for interacting with a Webthing.

        Args:
            webthing_fqdn (str): The fully quallified domain name e.g. 'webthing.example.com'.
            secure (bool, optional): If the Webthing uses TLS (https and wss). Defaults to True.
        """
        self._webthing_fqdn: str = webthing_fqdn.strip('/')
        self._secure = secure

        self._observation_callbacks: Dict[str, List[Callable[[str, Observation], None]]] = {}
        self._event_callbacks: List[Callable[[Event], None]] = []
        self._action_callbacks: List[Tuple[Callable[[Action], None], ActionType, bool]] = []
        self._actions_created: Set[int] = set()

        if self._secure:
            self._ws_uri = f"wss://{self._webthing_fqdn}/websocket-stomp"
        else:
            self._ws_uri = f"ws://{self._webthing_fqdn}/websocket-stomp"
        self._ws = StompWebsocket(self._ws_uri)

        if self._secure:
            self._webthing_url = f"https://{self._webthing_fqdn}"
        else:
            self._webthing_url = f"http://{self._webthing_fqdn}"

    def _process_observation(self, relative_uri: str, json_str: str) -> None:
        observation = Observation.from_json_observation_string(json_str)
        for callback in self._observation_callbacks.get(relative_uri, []):
            callback(relative_uri, observation)

    def _ws_subscribe(self, relative_uri: str, callback: Callable[[str, str], None]) -> str:
        # Websocket expects "absolute" uri, make this transparent to the user
        self._ws.subscribe(f"/{relative_uri}", lambda destination, message: callback(destination.lstrip('/'), message))

    def subscribe_resource(self, resource_uri: str, callback: Callable[[str, Observation], None]) -> str:
        """Subscribe to realtime Observations for the given resource.

        Args:
            resource_uri (str): The (relative) URI to the resource i.e. 'thing/123/property/123. Will be made relative if not.
            callback (Callable[[str, Observation], None]): Callback for new Observation. First argument is the relative URI subscribed to, equal to returned URI.

        Returns:
            str: Relative URI actually subscribed to.
        """ 
        # Return relative uri subsribed to
        relative_uri = get_relative_uri(resource_uri)
        if relative_uri not in self._observation_callbacks:
            self._ws_subscribe(relative_uri, self._process_observation)
        self._observation_callbacks.setdefault(relative_uri, []).append(callback)
        return relative_uri

    def _process_event(self, _: str, json_str: str) -> None:
        event = Event.from_json_observation_string(json_str)
        if event is not None:
            for callback in self._event_callbacks:
                callback(event)

    def subscribe_events(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to realtime Events.

        Args:
            callback (Callable[[Event], None]): Callback for new Events.
        """
        if len(self._event_callbacks) == 0:
            self._ws_subscribe(self._EVENTS_URI, self._process_event)
        self._event_callbacks.append(callback)

    def _process_action(self, _: str, json_str: str) -> None:
        action = Action.from_json_observation_string(json_str)
        if action is not None:
            self_created = action.hash() in self._actions_created
            self._actions_created.discard(action.hash())
            for callback, type, filter_created in self._action_callbacks:
                if type is None or type == action.TYPE:
                    if not self_created or not filter_created:
                        callback(action)

    def subscribe_actions(self, callback: Callable[[Action], None], type: ActionType=None, filter_created: bool=False) -> None:
        """Subscribe to realtime Actions.

        Args:
            callback (Callable[[Action], None]): Callback for new Actions.
            type (ActionType, optional): Only subscribe to given ActionType, None means all. Defaults to None.
            filter_created (bool, optional): If the webthing should filter Actions it produced itself. Defaults to False.
            In case of separate instances of WebthingClients Events produced by one will not be filtered out by the other.
        """
        if len(self._action_callbacks) == 0:
            self._ws_subscribe(self._ACTIONS_URI, self._process_action)
        self._action_callbacks.append((callback, type, filter_created))

    def _send_action(self, action: Action) -> bool:
        self._actions_created.add(action.hash())
        response = requests.post(f"{self._webthing_url}/{self._ACTIONS_URI}", json=action.get_value())
        return response.ok




    def send_create_event_action(self, event: Event, stream: bool=False) -> bool:
        """Send a CreateEventAction for the given Event.

        Args:
            event (Event): New Event.
            stream (bool, optional): If the event should be processed as realtime, only do this if near realtime. Defaults to False.

        Returns:
            bool: If the operation was successful.
        """
        action = CreateEventAction(None, event, stream)
        return self._send_action(action)


    def send_update_event_action(self, event: Event) -> bool:
        """Send a UpdateEventAction for the given Event.

        Args:
            event (Event): Updated Event.

        Returns:
            bool: If the operation was successful.
        """
        action = UpdateEventAction(None, event)
        return self._send_action(action)

    def send_delete_event_action(self, relative_uri: str) -> bool:
        """Send a DeleteEventAction for the given Event relative URI.

        Args:
            event (Event): Relative URI of the to be deleted event.

        Returns:
            bool: If the operation was successful.
        """
        action = DeleteEventAction(None, relative_uri)
        return self._send_action(action)
