from taktyk.reminder_repository import InMemoryReminderRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


class TestTaktyk(object):

    def test_get_reminders_from_more_then_one_page(self):
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        api.add_notification('login1', 'id-1', 'sub-id-1', 1)
        api.add_notification('login3', 'id-2', 'sub-id-1', 1)
        api.add_notification('login4', 'id-3', 'sub-id-1', 2)
        api.add_notification('login5', 'id-4', 'sub-id-1', 2)
        api.add_entry('id-1', 1)
        api.add_entry('id-2', 1)
        api.add_entry('id-3', 1)
        api.add_entry('id-4', 1)

        bot = TaktykBot(api, repository)
        bot.save_new_reminders()

        assert len(repository.get_all()) == 4

    def test_get_reminders_from_more_then_one_user_to_one_entry(self):
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        entry_id = 'id-1'
        api.add_notification('login1', entry_id, 'sub-id-1', 1)
        api.add_notification('login3', entry_id, 'sub-id-1', 1)
        api.add_entry(entry_id, 2)

        bot = TaktykBot(api, repository)
        bot.save_new_reminders()

        assert len(repository.get_all()) == 1
        assert len(repository.get_all()[0].logins_with_last_seen_comment_id) == 2
        assert repository.get_all()[0].comments_count == 2


