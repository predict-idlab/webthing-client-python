from typing import Callable, Dict, List
import threading
import time

from websocket import WebSocketApp, WebSocketException, enableTrace
import stomper


class StompWebsocket:
    """A class for setting up and managing a Stomp websocket."""
    
    def __init__(self, ws_uri: str, reconnect_timeout_ms: int=60_000, verbose: bool=False) -> None:
        """A class for setting up and managing a Stomp websocket.

        Args:
            ws_uri (str): The websocket URI to connect to, should be of protocol type 'ws://' or 'wss://' i.g. 'ws://webthing.example.com'.
            reconnect_timeout_ms (int, optional): Reconnect timeout. Defaults to 60_000.
            verbose (bool, optional): Verbose logging. Defaults to False.
        """
        self._ws_uri = ws_uri
        self._reconnect_timeout_ms = reconnect_timeout_ms
        self._verbose = verbose

        self._connected = False
        self._backlog_subscriptions: Dict[str, List[Callable[[str], None]]] = {}
        self._subscriptions: Dict[str, List[Callable[[str], None]]] = {}
        self._next_sub_id  = 0

        self._reconnect = False
        self._reconnect_status_code = None
        self._reconnect_message = None

        self._init_websocket()

    def __del__(self):
        # Close websocket
        self._ws.close()

    def _init_websocket(self) -> None:
        enableTrace(self._verbose)
        self._ws = WebSocketApp(self._ws_uri, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error, on_close=self._on_close)
        self._ws_thread = threading.Thread(target=self._ws.run_forever)
        self._ws_thread.start()

    def _on_open(self, ws: WebSocketApp):
        # Send stomp connect message on websocket open
        # We don't want to send heartbeats but want to receive heartbeats
        self._ws.send("CONNECT\naccept-version:1.1\nheart-beat:0,25000\n\n\x00\n")

    def _on_message(self, ws: WebSocketApp, stomp_message: str) -> None:
        # If an empty message it is a heartbeat
        if stomp_message.strip(" \n") == "":
            if self._verbose:
                print("Received heartbeat")
            return
        # Process stomp message from websocket
        message = stomper.Frame.unpack(stomper.Frame(), stomp_message)
        if message['cmd'] == 'CONNECTED':
            self._connected_message()
            if self._reconnect:
                print(f"WebsocketClient <{self._ws_uri}> reconnected")
            # Reset reconnect
            self._reconnect = False
            self._reconnect_error = None
            self._reconnect_status_code = None
            self._reconnect_message = None
            return
        elif message['cmd'] == 'MESSAGE':
            destination = message['headers']['destination']
            if destination != None and destination in self._subscriptions:
                callbacks = self._subscriptions[destination]
                # Call all callbacks
                for callback in callbacks:
                    callback(message['body'])

    def _connected_message(self):
        self._connected = True
        # Subscribe to backlog
        for destination, callbacks in self._backlog_subscriptions.items():
            for callback in callbacks:
                self._subscribe(destination, callback)
        self._backlog_subscriptions = {}

    def _on_error(self, ws: WebSocketApp, error: WebSocketException) -> None:
        if not self._reconnect:
            # If first error store
            self._reconnect_error = error
        else:
            print(f"WebsocketClient <{self._ws_uri}> error: {error}")

    def _on_close(self, ws: WebSocketApp, status_code: int, message: str) -> None:
        # Set connected to false and set backlog
        self._connected = False
        self._backlog_subscriptions.update(self._subscriptions)
        self._subscriptions = {}
        self._next_sub_id = 0

        # If first disconnect try to connect immediately, it may just be connection cleanup
        if not self._reconnect:
            self._reconnect = True
            self._reconnect_status_code = status_code
            self._reconnect_message = message
            self._init_websocket()
        else:
            print(f"WebsocketClient <{self._ws_uri}> closed with status {status_code} and message: {message}, retrying in {self._reconnect_timeout_ms/1000} seconds...")
            # Print first error
            if self._reconnect_error is not None:
                print(f"WebsocketClient <{self._ws_uri}> first error: {self._reconnect_error}")
                self._reconnect_error = None
            # Print first disconnect
            if self._reconnect_status_code is not None or self._reconnect_message is not None:
                print(f"WebsocketClient <{self._ws_uri}> first closed with status {self._reconnect_status_code} and message: {self._reconnect_message}")
                self._reconnect_status_code = status_code = None
                self._reconnect_message = message = None
            # Retry after timeout
            time.sleep(self._reconnect_timeout_ms/1000)
            self._init_websocket()


    def subscribe(self, destination: str, callback: Callable[[str], None]) -> None:
        """Subscribe to a destination on websocket.

        Args:
            destination (str): Destination string.
            callback (Callable[[str], None]): Callback for string message.
        """
        # If not yet connected push to backlog
        if self._connected == False:
            self._backlog_subscriptions.setdefault(destination, []).append(callback)
        else:
            self._subscribe(destination, callback)

    def _subscribe(self, destination: str, callback: Callable[[str], None]):
        # Subscribe if no subscriptions
        if len(self._subscriptions.get(destination, [])) == 0:
            self._ws.send(stomper.subscribe(destination, f"sub-{self._next_sub_id}", ack="auto"))
            self._next_sub_id += 1
        self._subscriptions.setdefault(destination, []).append(callback)

    def send(self, destination: str, message: str) -> None:
        """Send a message to websocket on provided destination.

        Args:
            destination (str): Destination string.
            message (str): The message to be sent.
        """
        self._ws.send(stomper.send(destination, message))
