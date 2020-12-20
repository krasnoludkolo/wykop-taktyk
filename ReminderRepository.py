from typing import NoReturn, List, Dict

from model import Reminder


class ReminderRepository:

    def save(self, reminder: Reminder) -> NoReturn:
        pass

    def add_nick_to_remainder(self, entry_id, nick):
        pass

    def set_reminder_comment_count(self, entry_id, comment_count):
        pass

    def get_comment_count(self, entry_id) -> int:
        pass

    def get_all(self) -> List[Reminder]:
        pass

    def has_entry(self, entry_id):
        pass


class InMemoryReminderRepository(ReminderRepository):

    def __init__(self):
        self.reminders: Dict[str, Reminder] = {}

    def save(self, reminder: Reminder) -> NoReturn:
        self.reminders[reminder.entry_id] = reminder

    def get_all(self) -> List[Reminder]:
        return list(self.reminders.values())

    def set_reminder_comment_count(self, entry_id, comment_count):
        self.reminders[entry_id].comments_count = comment_count

    def add_nick_to_remainder(self, entry_id, nick):
        self.reminders[entry_id].nicks.append(nick)

    def has_entry(self, entry_id):
        return entry_id in self.reminders

    def get_comment_count(self, entry_id) -> int:
        return self.reminders[entry_id].comments_count
