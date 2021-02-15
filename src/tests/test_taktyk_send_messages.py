from tests.wykop_api_test_utils import *


class TestTaktykSendMessages(object):

    def test_send_one_notification_about_new_comment(self):
        api, bot, login, repository = default_test_context()
        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)

        bot.run()

        new_comment_to_entry_is_added(api, entry_id)

        bot.run()

        assert messages_in_conversation(api, login) == 1

    def test_send_one_message_about_new_comment_if_user_observe_twice_same_entry(self):
        api, bot, login, repository = default_test_context()
        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        user_request_observation(api, entry_id, login)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert messages_in_conversation(api, login) == 1

    def test_send_message_with_link_to_last_read_comment(self):
        api, bot, login, repository = default_test_context()
        entry_id = new_entry_is_added(api)
        comment_id = user_request_observation(api, entry_id, login)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert f'https://www.wykop.pl/wpis/{entry_id}/#comment-{comment_id}' in api.conversation(login)[0]['body']

    def test_send_second_message_with_link_to_last_read_comment(self):
        api, bot, login, repository = default_test_context()
        entry_id = new_entry_is_added(api)
        comment_id_1 = user_request_observation(api, entry_id, login)
        bot.run()
        comment_id_2 = new_comment_to_entry_is_added(api, entry_id)

        bot.run()

        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert f'https://www.wykop.pl/wpis/{entry_id}/#comment-{comment_id_1}' in api.conversation(login)[0]['body']
        assert f'https://www.wykop.pl/wpis/{entry_id}/#comment-{comment_id_2}' in api.conversation(login)[1]['body']

    def test_send_correct_comment_id_for_different_users(self):
        api, bot, login, repository = default_test_context()
        different_login = 'different_login'
        entry_id = new_entry_is_added(api)

        login_comment_id = user_request_observation(api, entry_id, login)
        different_login_comment_id = user_request_observation(api, entry_id, different_login)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id)
        bot.run()

        assert f'https://www.wykop.pl/wpis/{entry_id}/#comment-{login_comment_id}' in api.conversation(login)[0][
            'body']
        assert f'https://www.wykop.pl/wpis/{entry_id}/#comment-{different_login_comment_id}' in \
               api.conversation(different_login)[-1]['body']

    def test_should_ignore_removed_entry(self):
        api, bot, login, _ = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        bot.run()

        entry_is_removed(api, entry_id)
        bot.run()
