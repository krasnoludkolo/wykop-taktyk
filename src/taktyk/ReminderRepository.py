from typing import NoReturn, List, Dict, Set

from taktyk.model import Reminder
import shelve


class ReminderRepository:

    def save(self, reminder: Reminder) -> NoReturn:
        pass

    def add_nicks_to_remainder(self, entry_id, nicks: Set[str]):
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

    def add_nicks_to_remainder(self, entry_id, nick: Set[str]):
        self.reminders[entry_id].nicks.update(nick)

    def has_entry(self, entry_id):
        return entry_id in self.reminders

    def get_comment_count(self, entry_id) -> int:
        return self.reminders[entry_id].comments_count


class ShelveReminderRepository(ReminderRepository):

    def __init__(self, filename: str):
        self.filename: str = filename

    def save(self, reminder: Reminder) -> NoReturn:
        with self.__file_db() as db:
            db[reminder.entry_id] = reminder

    def get_all(self) -> List[Reminder]:
        with self.__file_db() as db:
            return list(db.values())

    def set_reminder_comment_count(self, entry_id, comment_count):
        with self.__file_db() as db:
            db[entry_id].comments_count = comment_count

    def add_nicks_to_remainder(self, entry_id, nicks: Set[str]):
        with self.__file_db() as db:
            db[entry_id].nicks.update(nicks)

    def has_entry(self, entry_id):
        with self.__file_db() as db:
            return entry_id in db

    def get_comment_count(self, entry_id) -> int:
        with self.__file_db() as db:
            return db[entry_id].comments_count

    def __file_db(self):
        return shelve.open(self.filename, writeback=True)
