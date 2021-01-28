import logging
from typing import NoReturn, List, Dict, Set

from taktyk.model import Reminder
import shelve


class ReminderRepository:

    def save(self, reminder: Reminder) -> NoReturn:
        pass

    def add_login_to_remainder(self, entry_id, login_with_comment_id: Dict[str, str]):
        pass

    def set_reminder_comment_count(self, entry_id, comment_count):
        pass

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        pass

    def get_comment_count(self, entry_id) -> int:
        pass

    def get_all_actives(self) -> List[Reminder]:
        pass

    def has_entry(self, entry_id) -> bool:
        pass

    def remove_login_from_reminder(self, entry_id, login):
        pass

    def has_reminder_with_login(self, entry_id, login):
        pass

    def mark_as_inactive(self, entry_id):
        pass


class InMemoryReminderRepository(ReminderRepository):

    def __init__(self):
        self.reminders: Dict[str, Reminder] = {}

    def save(self, reminder: Reminder) -> NoReturn:
        self.reminders[reminder.entry_id] = reminder

    def get_all_actives(self) -> List[Reminder]:
        return list([reminder for reminder in self.reminders.values() if reminder.active])

    def set_reminder_comment_count(self, entry_id, comment_count):
        self.reminders[entry_id].comments_count = comment_count

    def add_login_to_remainder(self, entry_id, login_with_comment_id: Dict[str, str]):
        self.reminders[entry_id].logins_with_last_seen_comment_id.update(login_with_comment_id)

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        self.reminders[entry_id].logins_with_last_seen_comment_id.update({login: last_seen_comment_id})

    def has_entry(self, entry_id):
        return entry_id in self.reminders

    def get_comment_count(self, entry_id) -> int:
        return self.reminders[entry_id].comments_count

    def remove_login_from_reminder(self, entry_id, login):
        self.reminders[entry_id].logins_with_last_seen_comment_id.pop(login)

    def has_reminder_with_login(self, entry_id, login):
        if not self.has_entry(entry_id):
            return False
        return login in self.reminders[entry_id].logins_with_last_seen_comment_id.keys()

    def mark_as_inactive(self, entry_id):
        if self.has_entry(entry_id):
            self.reminders[entry_id].active = False
        else:
            logging.error(f'Try to mark as inactive non-existing reminder. Entry id: {entry_id}')


class ShelveReminderRepository(ReminderRepository):

    def __init__(self, filename: str):
        self.filename: str = filename

    def save(self, reminder: Reminder) -> NoReturn:
        with self.__file_db() as db:
            db[reminder.entry_id] = reminder

    def get_all_actives(self) -> List[Reminder]:
        with self.__file_db() as db:
            return list([reminder for reminder in db.values() if reminder.active])

    def set_reminder_comment_count(self, entry_id, comment_count):
        with self.__file_db() as db:
            db[entry_id].comments_count = comment_count

    def add_login_to_remainder(self, entry_id, login_with_comment_id: Dict[str, str]):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.update(login_with_comment_id)

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.update({login: last_seen_comment_id})

    def has_entry(self, entry_id):
        with self.__file_db() as db:
            return entry_id in db

    def get_comment_count(self, entry_id) -> int:
        with self.__file_db() as db:
            return db[entry_id].comments_count

    def remove_login_from_reminder(self, entry_id, login):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.pop(login)

    def has_reminder_with_login(self, entry_id, login):
        with self.__file_db() as db:
            if entry_id not in db:
                return False
            return login in db[entry_id].logins_with_last_seen_comment_id.keys()

    def mark_as_inactive(self, entry_id):
        with self.__file_db() as db:
            if entry_id in db:
                db[entry_id].active = False
            else:
                logging.error(f'Try to mark as inactive non-existing reminder. Entry id: {entry_id}')

    def __file_db(self):
        return shelve.open(self.filename, writeback=True)
