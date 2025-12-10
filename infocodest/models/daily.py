"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Daily(db.Model):
    """Data model for user accounts."""

    __tablename__ = "daily"

    id = db.Column(db.Integer, primary_key=True)
    aplicacion = db.Column(db.String(64), index=False, unique=True, nullable=False)
    repo = db.Column(db.Integer, index=True, unique=True, nullable=False)
    proveedor = db.Column(db.Text, index=False, unique=False, nullable=True)
    created_on = db.Column(db.DateTime(), unique=False, nullable=True)
    num_bugs = db.Column(db.Integer, index=False, unique=False, nullable=False)
    num_vulnerabilities = db.Column(db.Integer, index=False, unique=False, nullable=False)
    num_code_smells = db.Column(db.Integer, index=False, unique=False, nullable=False)
    num_quality = db.Column(db.Integer, index=False, unique=False, nullable=False)
    num_analisis = db.Column(db.Integer, index=False, unique=False, nullable=False)

    def __repr__(self):
        return "<Daily {}>".format(self.aplicacion)
    
    def to_dict(self):
        return {
                c.name: str(getattr(self, c.name)) for c in self.__table__.columns
        }
