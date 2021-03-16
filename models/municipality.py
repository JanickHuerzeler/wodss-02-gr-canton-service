from setup import db


class Municipality(db.Model):
    municipalityId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bfsNr = db.Column(db.Integer, nullable=False)
    zipCode = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    canton = db.Column(db.String(2), nullable=False)
    area = db.Column(db.Float, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(256), nullable=False)

    def __init__(self, bfsNr, date, incidence):
        self.bfsNr = bfsNr
        self.zipCode = zipCode
        self.name = name
        self.canton = canton
        self.area = area
        self.population = population
        self.region = region

    def __repr__(self):
        return '<Municipality %r>' % self.municipalityId

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'municipalityId': self.municipalityId,
            'bfsNr': self.bfsNr,
            'zipCode': self.zipCode,
            'name': self.name,
            'canton': self.canton,
            'area': self.area,
            'population': self.population,
            'region': self.region
        }