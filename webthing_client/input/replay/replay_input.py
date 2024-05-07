from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import List, Dict, Optional, Any

from webthing_client import utils


class ReplayInput:

    @classmethod
    def to_json_object(cls, from_historical: datetime,
                            to_historical: datetime,
                            from_replay: Optional[datetime],
                            speed_multiplier: Optional[float] = None,
                            loop: Optional[bool] = None,
                            scale_timestamps: Optional[bool] = None,
                            seconds_interval: Optional[int] = None,
                            replay_semantic_submissions_user_iris: Optional[List[str]] = None) -> Dict[str, Any]:
        return {
            'fromHistorical': utils.to_iso_time_format(from_historical),
            'toHistorical': utils.to_iso_time_format(to_historical),
            'fromReplay': utils.to_iso_time_format(from_replay),
            'speedMultiplier': speed_multiplier,
            'loop': loop,
            'scaleTimestamps': scale_timestamps,
            'secondsInterval': seconds_interval,
            'replaySemanticSubmissionsUser': replay_semantic_submissions_user_iris
        }
