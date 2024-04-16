from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import *

from ..ontology import WETHING_ONTOLOGY_PREFIX
from webthing_client import utils


class Replay:

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'Event'


    iri: str

    in_replay: bool
    """Indicating if currently in a replay."""
    
    from_historical: datetime
    """The historical window from."""

    from_replay: datetime
    """The current replay window from."""

    to_replay: datetime
    """The current replay window to."""

    loop: bool
    """Indicating if the replay is finished it should restart."""

    speed_scalar: int
    """The speed scalar, used with multiply to speed up or slow down replay"""

    speed_multiply: bool
    """True if the replay should be sped up by the speed scalar, false if it should be slowed down by speed scalar."""

    scale_timestamps: bool
    """If the transformed historical timestamps should be scaled depending on speed, if true will change the difference between timestamps,
    if false will just move timestamps in time by the difference between historical and replay windows."""

    seconds_interval: int
    """The polling interval to use."""

    replay_semantic_submissioons_user_iris: List[str]
    """The IRI's of the users whose semantic submissions (requests,actions,resolutions) we must replay."""

    def __init__(self, iri: str,
                 in_replay: bool,
                 from_historical: datetime,
                 from_replay: datetime,
                 to_replay: datetime,
                 loop: bool,
                 speed_scalar: int,
                 speed_multiply: bool,
                 scale_timestamps: bool,
                 seconds_interval: int,
                 replay_semantic_submissioons_user_iris: List[str]) -> None:
        self.iri = iri
        self.in_replay = in_replay
        self.from_historical = from_historical
        self.from_replay = from_replay
        self.to_replay = to_replay
        self.loop = loop
        self.speed_scalar = speed_scalar
        self.speed_multiply = speed_multiply
        self.scale_timestamps = scale_timestamps
        self.seconds_interval = seconds_interval
        self.replay_semantic_submissioons_user_iris = replay_semantic_submissioons_user_iris
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Replay:
        return cls(
            json_object['$iri'],
            json_object['inReplay'],
            utils.parse_iso_time_format(json_object['fromHistorical']),
            utils.parse_iso_time_format(json_object['fromReplay']),
            utils.parse_iso_time_format(json_object['toReplay']),
            json_object['loop'],
            json_object['speedScalar'],
            json_object['speedMultiply'],
            json_object['scaleTimestamps'],
            json_object['secondsInterval'],
            json_object['replaySemanticSubmissionsUser']
        )

    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'fromHistorical': utils.to_iso_time_format(self.from_historical),
            'fromReplay': utils.to_iso_time_format(self.from_replay),
            'toReplay': utils.to_iso_time_format(self.to_replay),
            'loop': self.loop,
            'speedScalar': self.speed_scalar,
            'speedMultiply': self.speed_multiply,
            'scaleTimestamps': self.scale_timestamps,
            'secondsInterval': self.seconds_interval,
            'replaySemanticSubmissionsUser': self.replay_semantic_submissioons_user_iris
        }
