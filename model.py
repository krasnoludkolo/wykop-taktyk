class Reminder:

    def __init__(self, nicks, entry_id, comment_id, comments_count) -> None:
        self.nicks = nicks if isinstance(nicks, list) else [nicks]
        self.entry_id = entry_id
        self.comment_id = comment_id
        self.comments_count = comments_count

    def __iter__(self):
        return iter((self.nicks, self.entry_id, self.comment_id, self.comments_count))

    def __str__(self) -> str:
        return f'Reminder({self.nicks}, {self.entry_id}, {self.comment_id}, {self.comments_count})'

    def __repr__(self) -> str:
        return f'Reminder({self.nicks}, {self.entry_id}, {self.comment_id}, {self.comments_count})'


entry_url = 'https://www.wykop.pl/wpis'
