import logging
import shelve
from typing import NoReturn, List, Dict

from taktyk.model import Observation


class ObservationRepository:

    def save(self, observation: Observation) -> NoReturn:
        pass

    def add_login_to_observation(self, entry_id, login_with_comment_id: Dict[str, str]):
        pass

    def set_observation_comment_count(self, entry_id, comment_count):
        pass

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        pass

    def get_comment_count(self, entry_id) -> int:
        pass

    def get_all_actives(self) -> List[Observation]:
        pass

    def has_entry(self, entry_id) -> bool:
        pass

    def remove_login_from_observation(self, entry_id, login):
        pass

    def has_observation_with_login(self, entry_id, login):
        pass

    def mark_as_inactive(self, entry_id):
        pass


class InMemoryObservationRepository(ObservationRepository):

    def __init__(self):
        self.observations: Dict[str, Observation] = {}

    def save(self, observation: Observation) -> NoReturn:
        self.observations[observation.entry_id] = observation

    def get_all_actives(self) -> List[Observation]:
        return list([observation for observation in self.observations.values() if observation.active])

    def set_observation_comment_count(self, entry_id, comment_count):
        self.observations[entry_id].comments_count = comment_count

    def add_login_to_observation(self, entry_id, login_with_comment_id: Dict[str, str]):
        self.observations[entry_id].logins_with_last_seen_comment_id.update(login_with_comment_id)

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        self.observations[entry_id].logins_with_last_seen_comment_id.update({login: last_seen_comment_id})

    def has_entry(self, entry_id):
        return entry_id in self.observations

    def get_comment_count(self, entry_id) -> int:
        return self.observations[entry_id].comments_count

    def remove_login_from_observation(self, entry_id, login):
        self.observations[entry_id].logins_with_last_seen_comment_id.pop(login)

    def has_observation_with_login(self, entry_id, login):
        if not self.has_entry(entry_id):
            return False
        return login in self.observations[entry_id].logins_with_last_seen_comment_id.keys()

    def mark_as_inactive(self, entry_id):
        if self.has_entry(entry_id):
            self.observations[entry_id].active = False
        else:
            logging.error(f'Try to mark as inactive non-existing observation. Entry id: {entry_id}')


class ShelveObservationRepository(ObservationRepository):

    def __init__(self, filename: str):
        self.filename: str = filename

    def save(self, observation: Observation) -> NoReturn:
        with self.__file_db() as db:
            db[observation.entry_id] = observation

    def get_all_actives(self) -> List[Observation]:
        with self.__file_db() as db:
            return list([observation for observation in db.values() if observation.active])

    def set_observation_comment_count(self, entry_id, comment_count):
        with self.__file_db() as db:
            db[entry_id].comments_count = comment_count

    def add_login_to_observation(self, entry_id, login_with_comment_id: Dict[str, str]):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.update(login_with_comment_id)

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.update({login: last_seen_comment_id})

    def has_entry(self, entry_id):
        with self.__file_db() as db:
            return entry_id in db

    def get_comment_count(self, entry_id) -> int:
        with self.__file_db() as db:
            return db[entry_id].comments_count

    def remove_login_from_observation(self, entry_id, login):
        with self.__file_db() as db:
            db[entry_id].logins_with_last_seen_comment_id.pop(login)

    def has_observation_with_login(self, entry_id, login):
        with self.__file_db() as db:
            if entry_id not in db:
                return False
            return login in db[entry_id].logins_with_last_seen_comment_id.keys()

    def mark_as_inactive(self, entry_id):
        with self.__file_db() as db:
            if entry_id in db:
                db[entry_id].active = False
            else:
                logging.error(f'Try to mark as inactive non-existing observation. Entry id: {entry_id}')

    def __file_db(self):
        return shelve.open(self.filename, writeback=True)
