from typing import Set, Dict


class Reminder:

    def __init__(self, nicks_with_last_seen_comment_id: Dict[str, str], entry_id: str, comment_id: str,
                 comments_count: int) -> None:
        self.entry_id: str = entry_id
        self.comment_id: str = comment_id
        self.comments_count: int = comments_count
        self.nicks_with_last_seen_comment_id: Dict[str, str] = nicks_with_last_seen_comment_id

    def __iter__(self):
        return iter((self.nicks_with_last_seen_comment_id, self.entry_id, self.comment_id, self.comments_count))

    def __str__(self) -> str:
        return f'Reminder({self.nicks_with_last_seen_comment_id}, {self.entry_id}, {self.comment_id}, {self.comments_count})'

    def __repr__(self) -> str:
        return f'Reminder({self.nicks_with_last_seen_comment_id}, {self.entry_id}, {self.comment_id}, {self.comments_count})'


entry_url = 'https://www.wykop.pl/wpis'
