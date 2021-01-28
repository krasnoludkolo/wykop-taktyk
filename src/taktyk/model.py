from typing import Dict

from taktyk.python_utils import auto_str, auto_repr


@auto_str
@auto_repr
class Reminder:

    def __init__(self, logins_with_last_seen_comment_id: Dict[str, str], entry_id: str, comment_id: str,
                 comments_count: int) -> None:
        self.entry_id: str = entry_id
        self.comment_id: str = comment_id
        self.comments_count: int = comments_count
        self.logins_with_last_seen_comment_id: Dict[str, str] = logins_with_last_seen_comment_id
        self.active = True

    def __iter__(self):
        return iter(
            (self.logins_with_last_seen_comment_id, self.entry_id, self.comment_id, self.comments_count, self.active))


@auto_str
@auto_repr
class ReminderCandidate:

    def __init__(self, login: str, entry_id: str, comment_id: str, comments_count: int) -> None:
        self.comment_id: str = comment_id
        self.login: str = login
        self.entry_id: str = entry_id
        self.comment_id: str = comment_id
        self.comments_count: int = comments_count

    def __iter__(self):
        return iter((self.login, self.entry_id, self.comment_id, self.comments_count))
