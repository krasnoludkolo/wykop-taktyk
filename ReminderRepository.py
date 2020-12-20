from typing import NoReturn, List

from model import Reminder


class ReminderRepository:

    def save(self, reminder: Reminder) -> NoReturn:
        pass

    def get_all(self) -> List[Reminder]:
        pass


class InMemoryReminderRepository(ReminderRepository):

    def __init__(self):
        self.reminders = []

    def save(self, reminder: Reminder) -> NoReturn:
        self.reminders.append(reminder)

    def get_all(self) -> List[Reminder]:
        return self.reminders
