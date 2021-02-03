import logging
import shelve
from typing import NoReturn, List, Dict

from taktyk.model import Observation, LoginObservation, ObservationMode


class ObservationRepository:

    def save(self, observation: Observation) -> NoReturn:
        pass

    def add_login_to_observation(self, entry_id, login_observation: LoginObservation) -> NoReturn:
        pass

    def set_observation_comment_count(self, entry_id, comment_count) -> NoReturn:
        pass

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str) -> NoReturn:
        pass

    def get_comment_count(self, entry_id) -> int:
        pass

    def get_all_actives(self) -> List[Observation]:
        pass

    def has_entry(self, entry_id) -> bool:
        pass

    def remove_login_from_observation(self, entry_id, login) -> NoReturn:
        pass

    def has_observation_with_login(self, entry_id, login) -> bool:
        pass

    def mark_as_inactive(self, entry_id) -> NoReturn:
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

    def add_login_to_observation(self, entry_id, login_observation: LoginObservation):
        login = login_observation.login
        self.observations[entry_id].login_observations.update({login: login_observation})

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        self.observations[entry_id].login_observations[login].last_seen_comment_id = last_seen_comment_id

    def has_entry(self, entry_id):
        return entry_id in self.observations

    def get_comment_count(self, entry_id) -> int:
        return self.observations[entry_id].comments_count

    def remove_login_from_observation(self, entry_id, login):
        self.observations[entry_id].login_observations.pop(login)

    def has_observation_with_login(self, entry_id, login):
        if not self.has_entry(entry_id):
            return False
        return login in self.observations[entry_id].login_observations.keys()

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
            model = to_db_model(observation)
            db[observation.entry_id] = model

    def get_all_actives(self) -> List[Observation]:
        with self.__file_db() as db:
            observations = list(db.values()).copy()
            result = [to_domain_model(observation) for observation in observations if observation['active']]
            return result

    def set_observation_comment_count(self, entry_id, comment_count):
        with self.__file_db() as db:
            db[entry_id]['comments_count'] = comment_count

    def add_login_to_observation(self, entry_id, login_observation: LoginObservation):
        with self.__file_db() as db:
            db[entry_id]['login_observations'].update({login_observation.login: to_db_model(login_observation)})

    def set_last_seen_id_for_login(self, entry_id, login: str, last_seen_comment_id: str):
        with self.__file_db() as db:
            db[entry_id]['login_observations'][login]['last_seen_comment_id'] = last_seen_comment_id

    def has_entry(self, entry_id):
        with self.__file_db() as db:
            return entry_id in db

    def get_comment_count(self, entry_id) -> int:
        with self.__file_db() as db:
            return db[entry_id]['comments_count']

    def remove_login_from_observation(self, entry_id, login):
        with self.__file_db() as db:
            db[entry_id]['login_observations'].pop(login)

    def has_observation_with_login(self, entry_id, login):
        with self.__file_db() as db:
            if entry_id not in db:
                return False
            return login in db[entry_id]['login_observations'].keys()

    def mark_as_inactive(self, entry_id):
        with self.__file_db() as db:
            if entry_id in db:
                db[entry_id]['active'] = False
            else:
                logging.error(f'Try to mark as inactive non-existing observation. Entry id: {entry_id}')

    def __file_db(self):
        return shelve.open(self.filename, writeback=True)


def to_db_model(x: any) -> Dict[str, any]:
    if isinstance(x, (Observation, LoginObservation, Dict)):
        result: Dict = x.__dict__ if not isinstance(x, Dict) else x
        for k, v in result.items():
            if isinstance(v, (Observation, LoginObservation, Dict)):
                result.update({k: to_db_model(v)})
            if k == 'observation_mode':
                result.update({k: v.value})
        return result
    raise Exception


def to_domain_model(model: Dict[str, any]) -> Observation:
    observation = empty_observation()
    observation.__dict__.update(model.copy())
    observation.login_observations = {}
    for login, value in model['login_observations'].items():
        o = create_login_observation(value)
        observation.login_observations.update({login: o})
    return observation


def empty_observation():
    return Observation(None, None, None, None)


def create_login_observation(value):
    o = LoginObservation(value['login'], value['last_seen_comment_id'], ObservationMode(int(value['observation_mode'])))
    return o
