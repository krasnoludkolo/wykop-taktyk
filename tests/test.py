from ReminderRepository import InMemoryReminderRepository
from TaktykBot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


class Test(object):

    def test_get_notifications_from_more_then_one_page(self):
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        entry_id = 'id-1'
        api.add_notification('login1', entry_id, 'sub-id-1', 1)
        api.add_notification('login3', entry_id, 'sub-id-1', 1)
        api.add_notification('login4', entry_id, 'sub-id-1', 2)
        api.add_notification('login5', entry_id, 'sub-id-1', 2)
        api.add_entry(entry_id, 4)

        bot = TaktykBot(api, repository)
        bot.save_new_reminders()

        assert len(repository.get_all()) == 4
