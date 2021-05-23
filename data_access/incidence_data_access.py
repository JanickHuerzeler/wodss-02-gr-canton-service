from typing import List
from models.incidence import Incidence
from app import db
from sqlalchemy import and_

class IncidenceDataAccess:
    @staticmethod
    def get_all(date_from, date_to) -> List[Incidence]:
        incidences = (db.session.query(Incidence)
            .filter(Incidence.date.between(date_from, date_to))
            .order_by(Incidence.date.asc(), Incidence.bfsNr.asc())
        )

        return incidences


    @staticmethod
    def get(bfs_nr, date_from, date_to) -> List[Incidence]:
        incidences = (db.session.query(Incidence)
            .filter(and_(
                Incidence.bfsNr == bfs_nr,
                Incidence.date.between(date_from, date_to)
                )
            )
            .order_by(Incidence.date.asc())
        )

        return incidences