from taktyk.reminder_repository import InMemoryReminderRepository
from taktyk.taktyk_bot import TaktykBot
from tests.FakeWykopApi import FakeWykopApi


class TestTaktykSendMessages(object):

    def test_send_one_notification_about_new_comment(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_notification(login, entry_id, 'sub-id-1', 1)
        api.add_entry(entry_id, start_comments_count)
        bot.run()

        api.set_entry_comments_count(entry_id, start_comments_count + 1)
        bot.run()

        assert len(api.conversation(login)) == 1

    def test_send_one_message_about_new_comment_if_user_observe_twice_same_entry(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_entry(entry_id, start_comments_count)
        api.add_notification(login, entry_id, 'sub-id-1', 1)
        api.add_notification(login, entry_id, 'sub-id-2', 1)
        bot.run()

        api.set_entry_comments_count(entry_id, start_comments_count + 2)
        bot.run()

        assert len(api.conversation(login)) == 1

    def test_send_message_with_link_to_last_read_comment(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_entry(entry_id, start_comments_count)
        api.add_notification(login, entry_id, 'sub-id-0', 1)
        bot.run()

        api.set_entry_comments_count(entry_id, start_comments_count + 2)
        bot.run()

        assert 'https://www.wykop.pl/wpis/id-1#comment-sub-id-0' in api.conversation(login)[0]['body']

    def test_send_second_message_with_link_to_last_read_comment(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login = 'login1'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_entry(entry_id, start_comments_count)
        api.add_notification(login, entry_id, 'sub-id-0', 1)
        bot.run()
        api.set_entry_comments_count(entry_id, start_comments_count + 1)

        bot.run()

        api.set_entry_comments_count(entry_id, start_comments_count + 2)
        bot.run()

        assert 'https://www.wykop.pl/wpis/id-1#comment-sub-id-0' in api.conversation(login)[0]['body']
        assert 'https://www.wykop.pl/wpis/id-1#comment-sub-id-1' in api.conversation(login)[1]['body']

    def test_send_correct_comment_id_for_different_users(self):
        entry_id = 'id-1'
        start_comments_count = 1
        login1 = 'login1'
        login2 = 'login2'
        repository = InMemoryReminderRepository()
        api = FakeWykopApi()
        bot = TaktykBot(api, repository)

        api.add_entry(entry_id, start_comments_count)
        api.add_notification(login1, entry_id, 'sub-id-0', 1)
        api.add_notification(login2, entry_id, 'sub-id-1', 1)
        api.set_entry_comments_count(entry_id, start_comments_count + 2)
        bot.run()

        api.set_entry_comments_count(entry_id, start_comments_count + 3)
        bot.run()

        assert 'https://www.wykop.pl/wpis/id-1#comment-sub-id-0' in api.conversation(login1)[-1]['body']
        assert 'https://www.wykop.pl/wpis/id-1#comment-sub-id-1' in api.conversation(login2)[-1]['body']