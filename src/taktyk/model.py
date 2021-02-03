from enum import Enum
from typing import Dict

from taktyk.python_utils import auto_str, auto_repr


class ObservationMode(Enum):
    ALL = 1
    OP = 2


@auto_str
@auto_repr
class LoginObservation:

    def __init__(self, login: str, last_seen_comment_id: str, observation_mode: ObservationMode) -> None:
        self.login: str = login
        self.last_seen_comment_id: str = str(last_seen_comment_id)
        self.observation_mode: ObservationMode = observation_mode


@auto_str
@auto_repr
class Observation:

    def __init__(self, login_observations: Dict[str, LoginObservation], entry_id: str, comment_id: str,
                 comments_count: int) -> None:
        self.entry_id: str = entry_id
        self.comment_id: str = comment_id
        self.comments_count: int = comments_count
        self.login_observations: Dict[str, LoginObservation] = login_observations
        self.active: bool = True

    def __iter__(self):
        return iter(
            (self.login_observations,
             self.entry_id,
             self.comment_id,
             self.comments_count,
             self.active))


@auto_str
@auto_repr
class ObservationCandidate:

    def __init__(self, login: str, entry_id: str, comment_id: str, comments_count: int,
                 observation_mode: ObservationMode = ObservationMode.ALL) -> None:
        self.login: str = login
        self.comment_id: str = str(comment_id)
        self.entry_id: str = str(entry_id)
        self.comment_id: str = str(comment_id)
        self.comments_count: int = comments_count
        self.observation_mode: ObservationMode = observation_mode

    def __iter__(self):
        return iter(
            (self.login,
             self.entry_id,
             self.comment_id,
             self.comments_count,
             self.observation_mode))
