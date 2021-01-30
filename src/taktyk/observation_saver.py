import logging
from typing import List

from wykop import WykopAPI

from taktyk.model import ObservationCandidate, Observation
from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import all_new, is_notification_new, observation_data_from_notification, \
    comment_count_from_entry, is_notification_comment_directed


class ObservationSaver:

    def __init__(self, api: WykopAPI, repo: ObservationRepository):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo

    def save_new_observations(self):
        for login, entry_id, comment_id, comments_count in self.__new_observations():
            if self.repo.has_entry(entry_id):
                self.__update_login_observation(comments_count, entry_id, {login: comment_id})
            else:
                self.__save_new_observation(comment_id, comments_count, entry_id, {login: comment_id})
        self.api.notification_mark_all_as_read()

    def __new_observations(self) -> List[ObservationCandidate]:
        result = []
        for n in self.__new_notifications():
            entry_id, login, comment_id = observation_data_from_notification(n)
            entry = self.api.entry(entry_id)
            comments_count = comment_count_from_entry(entry)
            observation = ObservationCandidate(login, entry_id, comment_id, comments_count)
            result.append(observation)
        return result

    def __new_notifications(self, page=1) -> List:
        notifications = [n for n in self.api.notifications_direct(page) if is_notification_comment_directed(n)]
        result = []
        if all_new(notifications):
            result += self.__load_next_page(page)
        result += notifications
        return [n for n in result if is_notification_new(n)]

    def __load_next_page(self, page):
        return self.__new_notifications(page + 1)

    def __update_login_observation(self, comments_count, entry_id, login_with_last_seen_comment_id):
        self.repo.add_login_to_observation(entry_id, login_with_last_seen_comment_id)
        saved_comments_count = self.repo.get_comment_count(entry_id)
        self.repo.set_observation_comment_count(entry_id, max(saved_comments_count, comments_count))
        logging.info(f'observation update: {entry_id} {max(saved_comments_count, comments_count)}')

    def __save_new_observation(self, comment_id, comments_count, entry_id, login_with_last_seen_comment_id):
        observation = Observation(login_with_last_seen_comment_id, entry_id, comment_id, comments_count)
        self.repo.save(observation)
        logging.info(f'new observation: {observation}')
