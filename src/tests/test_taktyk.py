from tests.wykop_api_test_utils import *


class TestTaktyk(object):

    def test_get_observations_from_more_then_one_page(self):
        api, bot, login, repository, start_comments_count = default_test_context()

        id_1 = new_entry_is_added(api, start_comments_count)
        id_2 = new_entry_is_added(api, start_comments_count)
        id_3 = new_entry_is_added(api, start_comments_count)
        id_4 = new_entry_is_added(api, start_comments_count)
        user_request_observation(api, id_1, login, page=1)
        user_request_observation(api, id_2, login, page=1)
        user_request_observation(api, id_3, login, page=2)
        user_request_observation(api, id_4, login, page=2)

        bot.run()

        assert len(repository.observations) == 4

    def test_get_observations_from_more_then_one_user_to_one_entry(self):
        api, bot, login, repository, start_comments_count = default_test_context()

        entry_id = new_entry_is_added(api, start_comments_count)
        user_request_observation(api, entry_id, 'login1')
        user_request_observation(api, entry_id, 'login2')

        bot.run()

        assert len(repository.get_all_actives()) == 1
        observation = list(repository.get_all_actives())[0]
        assert len(observation.logins_with_last_seen_comment_id) == 2
        assert observation.comments_count == start_comments_count + 2 * USER_OBSERVATION_REQUEST

    def test_should_not_take_read_notification_again(self):
        api, bot, login, repository, start_comments_count = default_test_context()

        entry_id = new_entry_is_added(api, start_comments_count)
        user_request_observation(api, entry_id, 'login1')

        bot.run()
        bot.run()

        assert len(list(repository.get_all_actives())) == 1
