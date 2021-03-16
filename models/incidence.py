from setup import db


class Incidence(db.Model):
    incidencesId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bfsNr = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    incidence = db.Column(db.Float, nullable=False)

    def __init__(self, bfsNr, date, incidence):
        self.bfsNr = bfsNr
        self.date = date
        self.incidence = incidence

    def __repr__(self):
        return '<Incidence %r>' % self.incidencesId

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'incidencesId': self.incidencesId,
            'bfsNr': self.bfsNr,
            'date': self.date,
            'incidence': self.incidence
        }
