from tests.wykop_api_test_utils import *


class TestTaktyk(object):

    def test_get_observations_from_more_then_one_page(self):
        api, bot, login, repository = default_test_context()

        id_1 = new_entry_is_added(api)
        id_2 = new_entry_is_added(api)
        id_3 = new_entry_is_added(api)
        id_4 = new_entry_is_added(api)
        user_request_observation(api, id_1, login, page=1)
        user_request_observation(api, id_2, login, page=1)
        user_request_observation(api, id_3, login, page=2)
        user_request_observation(api, id_4, login, page=2)

        bot.run()

        assert len(repository.get_all_actives()) == 4

    def test_get_observations_from_more_then_one_user_to_one_entry(self):
        api, bot, login, repository = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, 'login1')
        user_request_observation(api, entry_id, 'login2')

        bot.run()

        assert len(repository.get_all_actives()) == 1
        observation = list(repository.get_all_actives())[0]
        assert len(observation.login_observations) == 2
        assert observation.comments_count == 2 * USER_OBSERVATION_REQUEST

    def test_should_not_take_read_notification_again(self):
        api, bot, login, repository = default_test_context()

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, 'login1')

        bot.run()
        bot.run()

        assert len(list(repository.get_all_actives())) == 1
        assert len(list(repository.get_all_actives()[0].login_observations)) == 1

    def test_should_not_send_message_if_last_message_is_from_observer(self):
        api, bot, login, repository = default_test_context()
        different_user = 'different_user'

        entry_id = new_entry_is_added(api)
        user_request_observation(api, entry_id, login)
        user_request_observation(api, entry_id, different_user)
        bot.run()

        new_comment_to_entry_is_added(api, entry_id, different_user)
        new_comment_to_entry_is_added(api, entry_id, login)
        bot.run()

        assert messages_in_conversation(api, login) == NO_MESSAGE
        assert messages_in_conversation(api, different_user) == OBSERVATION_MESSAGE
