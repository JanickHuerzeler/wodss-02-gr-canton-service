from data_access.incidence_data_access import IncidenceDataAccess
from typing import List
from models.incidence import Incidence


class IncidenceService:
    @staticmethod
    def get_all(date_from, date_to) -> List[Incidence]:
        incidences = IncidenceDataAccess.get_all(date_from, date_to)
        result = []
        for i in incidences:
            result.append(i.serialize)
        return result


    @staticmethod
    def get(bfs_nr, date_from, date_to) -> List[Incidence]:
        incidences = IncidenceDataAccess.get(bfs_nr, date_from, date_to)
        result = []
        for i in incidences:
            result.append(i.serialize)
        return result
