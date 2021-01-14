from taktyk.ReminderRepository import InMemoryReminderRepository
from taktyk.TaktykBot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


# Fix impost
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
        assert len(repository.get_all()[0].nicks) == 2
        assert repository.get_all()[0].comments_count == 2

    def test_send_one_notification_about_new_comment(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_notification(login, entry_id, 'sub-id-1', 1)
        api.add_entry(entry_id, start_comments_count)
        bot.save_new_reminders()

        api.set_entry_comments_count(entry_id, start_comments_count + 1)
        bot.send_reminders()
        bot.send_reminders()

        assert len(api.get_sent_messages()[login]) == 1

    def test_send_one_notification_about_new_comment_if_user_observe_twice_same_entity(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_notification(login, entry_id, 'sub-id-1', 1)
        api.add_notification(login, entry_id, 'sub-id-2', 1)
        api.add_entry(entry_id, start_comments_count)
        bot.save_new_reminders()

        api.set_entry_comments_count(entry_id, start_comments_count + 2)
        bot.send_reminders()

        assert len(api.get_sent_messages()[login]) == 1
