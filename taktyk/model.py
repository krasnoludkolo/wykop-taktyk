from typing import Set


class Reminder:

    def __init__(self, nicks: Set[str], entry_id: str, comment_id: str, comments_count: int) -> None:
        self.nicks: Set[str] = nicks if isinstance(nicks, Set) else {nicks}
        self.entry_id: str = entry_id
        self.comment_id: str = comment_id
        self.comments_count: int = comments_count

    def __iter__(self):
        return iter((self.nicks, self.entry_id, self.comment_id, self.comments_count))

    def __str__(self) -> str:
        return f'Reminder({self.nicks}, {self.entry_id}, {self.comment_id}, {self.comments_count})'

    def __repr__(self) -> str:
        return f'Reminder({self.nicks}, {self.entry_id}, {self.comment_id}, {self.comments_count})'


entry_url = 'https://www.wykop.pl/wpis'
