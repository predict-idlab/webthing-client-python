from datetime import datetime
import json
from typing import *

from webthing_client.client import WebthingReplayClient
from webthing_client.model.replay.replay import Replay


def set_basic_replay_and_start(webthing_fqdn: str, from_historical: datetime, to_historical: datetime) -> None:
    """Set and start a basic replay.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        from_historical (datetime): Historical window start
        to_historical (datetime): Historical window stop
    """
    client = WebthingReplayClient(webthing_fqdn)
    client.set_replay(from_historical, to_historical)
    replay_status: Replay = client.start_replay()
    
    print(f"Status of replay:\n{json.dumps(replay_status.to_json_object())}")

def stop_replay(webthing_fqdn: str) -> None:
    """Stop any running replay.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingReplayClient(webthing_fqdn)
    replay_status: Replay = client.stop_replay()
    print(f"Status of replay:\n{json.dumps(replay_status.to_json_object())}")
