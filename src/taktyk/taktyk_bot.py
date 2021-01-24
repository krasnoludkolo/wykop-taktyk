from wykop import WykopAPI

from taktyk.message_sender import MessageSender
from taktyk.remiders_sender import RemindersSender
from taktyk.reminder_repository import ReminderRepository
from taktyk.reminders_remover import RemindersRemover
from taktyk.saver import ReminderSaver


class TaktykBot:

    def __init__(self, api: WykopAPI, repo: ReminderRepository):
        self.api: WykopAPI = api
        self.repo: ReminderRepository = repo
        self.reminder_saver = ReminderSaver(api, repo)
        self.message_sender = MessageSender(api)
        self.reminders_remover = RemindersRemover(api, repo, self.message_sender)
        self.reminders_sender = RemindersSender(api, repo, self.message_sender)

    def run(self):
        self.reminder_saver.save_new_reminders()
        self.reminders_remover.remove_reminders_from_messages()
        self.reminders_sender.send_reminders()
