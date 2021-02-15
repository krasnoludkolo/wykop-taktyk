from typing import List

from wykop import WykopAPI

from taktyk.base_logger import logger
from taktyk.model import ObservationCandidate, Observation, LoginObservation, ObservationMode
from taktyk.observation_repository import ObservationRepository
from taktyk.wykop_api_utils import all_new, is_notification_new, observation_data_from_notification, \
    comment_count_from_entry, is_notification_comment_directed, body_from_comment_with_id


def get_mode_from_comment(message) -> ObservationMode:
    if " op" in message:
        return ObservationMode.OP
    return ObservationMode.ALL


class ObservationSaver:

    def __init__(self, api: WykopAPI, repo: ObservationRepository):
        self.api: WykopAPI = api
        self.repo: ObservationRepository = repo

    def save_new_observations(self):
        observations_candidates = self.__new_observations_candidates()
        logger.debug(f'Found {len(observations_candidates)} observations candidates')
        for observation_candidate in observations_candidates:
            login, entry_id, comment_id, comments_count, mode = observation_candidate
            logger.debug(f'Processing {login} to {entry_id} entry id')
            if self.repo.has_entry(entry_id):
                login_observation = LoginObservation(login, comment_id, mode)
                self.__update_login_observation(comments_count, entry_id, login_observation)
            else:
                self.__save_new_observation(observation_candidate)

    def __new_observations_candidates(self) -> List[ObservationCandidate]:
        result = []
        for n in self.__new_notifications():
            entry_id, login, comment_id = observation_data_from_notification(n)
            entry = self.api.entry(entry_id)
            comments_count = comment_count_from_entry(entry)
            mode = get_mode_from_comment(body_from_comment_with_id(entry, comment_id))
            observation = ObservationCandidate(login, entry_id, comment_id, comments_count, mode)
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

    def __update_login_observation(self, comments_count: int, entry_id: str, login_observation: LoginObservation):
        self.repo.add_login_to_observation(entry_id, login_observation)
        saved_comments_count = self.repo.get_comment_count(entry_id)
        logger.info(f'observation update: {entry_id} {max(saved_comments_count, comments_count)}')

    def __save_new_observation(self, observation_candidate: ObservationCandidate):
        login, entry_id, comment_id, comments_count, mode = observation_candidate
        login_observations = {login: LoginObservation(login, comment_id, mode)}
        observation = Observation(login_observations, entry_id, comment_id, comments_count)
        self.repo.save(observation)
        logger.info(f'new observation: {observation}')
