from ReminderRepository import ReminderRepository
from model import Reminder


class FakeRepository(ReminderRepository):

    def __init__(self) -> None:
        self.db = {}

    def save(self, r: Reminder):
        self.db[r.entry_id] = r

    def get_all(self):
        return list(self.db.values())
