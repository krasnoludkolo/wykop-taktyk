from taktyk.model import Observation
from taktyk.observation_repository import ObservationRepository


class FakeRepository(ObservationRepository):

    def __init__(self) -> None:
        self.db = {}

    def save(self, o: Observation):
        self.db[o.entry_id] = o

    def get_all(self):
        return list(self.db.values())
