from typing import List
from models.municipality import Municipality
from app import db


class MunicipalityService:
    @staticmethod
    def get_all() -> List[Municipality]:
        municipalities = db.session.query(
            Municipality).order_by(Municipality.bfsNr.asc())

        result = []
        for m in municipalities:
            result.append(m.serialize)
        return result

    @staticmethod
    def get(bfs_nr) -> object:
        municipality = db.session.query(Municipality).filter(Municipality.bfsNr == bfs_nr).first()
        return municipality.serialize if municipality else None
