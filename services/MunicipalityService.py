from typing import List
from models.municipality import Municipality
from setup import db


class MunicipalityService:
    @staticmethod
    def get_all() -> List[Municipality]:
        municipalities = db.session.query(Municipality).all()

        result = []
        for m in municipalities:
            result.append(m.serialize)
        return result

    @staticmethod
    def get(bfs_nr) -> object:
        municipalities = db.session.query(Municipality).filter(Municipality.bfsNr == bfs_nr)

        result = []
        for m in municipalities:
            result.append(m.serialize)

        return result
