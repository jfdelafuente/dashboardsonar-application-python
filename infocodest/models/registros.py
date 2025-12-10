"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Registro(db.Model):
    """Data model for user accounts."""

    __tablename__ = "registro"

    id = db.Column(db.Integer, primary_key=True)
    proceso = db.Column(db.String(64), unique=True, nullable=False)
    created_on = db.Column(db.DateTime(), unique=False, nullable=True)
    num_app = db.Column(db.Integer, index=True, unique=True, nullable=False)
    num_repo = db.Column(db.Integer, index=True, unique=True, nullable=False)
    num_bugs = db.Column(db.Integer, index=True, unique=True, nullable=False)
    num_quality = db.Column(db.Integer, index=True, unique=True, nullable=False)
    num_analisis = db.Column(db.Integer, index=True, unique=True, nullable=True)
    
    def __repr__(self):
        return "<Registro {}>".format(self.aplicacion)
    
    def to_dict(self):
        return {
                c.name: str(getattr(self, c.name)) for c in self.__table__.columns
            }