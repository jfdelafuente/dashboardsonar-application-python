"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Proveedor(db.Model):
    """Data model for user accounts."""

    __tablename__ = "proveedor"

    id = db.Column(db.Integer, primary_key=True)
    aplicacion = db.Column(db.String(64), index=False, unique=True, nullable=False)
    proveedor = db.Column(db.Text, index=False, unique=False, nullable=True)
    tipo = db.Column(db.Text, index=False, unique=False, nullable=True)


    def __repr__(self):
        return "<Proveedor {}>".format(self.aplicacion)

    def to_dict(self):
        return {
                c.name: str(getattr(self, c.name)) for c in self.__table__.columns
            }
