from app import db
from configManager import ConfigManager

df = ConfigManager.get_instance().get_required_date_format()


class Incidence(db.Model):
    incidencesId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bfsNr = db.Column(db.Integer, db.ForeignKey("municipality.bfsNr"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    cases = db.Column(db.Integer, nullable=True)
    cases_cumsum_14d = db.Column(db.Integer, nullable=False)
    incidence = db.Column(db.Float, nullable=False)
    __table_args__ = (db.UniqueConstraint('bfsNr', 'date', name='_bfsNr_date_uc'),)

    def __init__(self, bfsNr, date, cases, cases_cumsum_14d, incidence):
        self.bfsNr = bfsNr
        self.date = date
        self.cases = cases
        self.cases_cumsum_14d = cases_cumsum_14d
        self.incidence = incidence

    def __repr__(self):
        return '<Incidence %r>' % self.incidencesId

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'bfsNr': self.bfsNr,
            'date': self.date.strftime(df),
            'incidence': self.incidence
        }
