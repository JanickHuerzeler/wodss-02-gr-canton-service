from data_access.municipality_data_access import MunicipalityDataAccess
from typing import List
from models.municipality import Municipality


class MunicipalityService:
    @staticmethod
    def get_all() -> List[Municipality]:
        result = []
        municipalities = MunicipalityDataAccess.get_all()
        for m in municipalities:
            result.append(m.serialize)
        return result

    @staticmethod
    def get(bfs_nr) -> Municipality:
        municipality = MunicipalityDataAccess.get(bfs_nr)
        return municipality.serialize if municipality else None
