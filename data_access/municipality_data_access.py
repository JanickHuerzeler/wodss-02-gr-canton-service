from typing import List
from models.municipality import Municipality
from app import db

class MunicipalityDataAccess:
    @staticmethod
    def get_all() -> List[Municipality]:
        municipalities = (db.session.query(Municipality)
                            .order_by(Municipality.bfsNr.asc())
                        )

        return municipalities


    @staticmethod
    def get(bfs_nr) -> Municipality:
        municipality = (db.session.query(Municipality)
                            .filter(Municipality.bfsNr == bfs_nr)
                            .first()
                        )
        return municipality