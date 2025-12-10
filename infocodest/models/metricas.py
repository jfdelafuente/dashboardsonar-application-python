"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Metrica(db.Model):
    """Data model for user accounts."""

    __tablename__ = "metricas"

    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(64), unique=True, nullable=False)
    aplicacion = db.Column(db.String(64), unique=False, nullable=True)
    fecha = db.Column(db.String(64), unique=False, nullable=True)
    bugs = db.Column(db.Integer, index=True, unique=True, nullable=False)
    reliability_rating = db.Column(db.Integer, index=True, unique=True, nullable=False)
    reliability_label = db.Column(db.String(64), unique=False, nullable=True)
    vulnerabilities = db.Column(db.Integer, index=True, unique=True, nullable=False)
    security_rating = db.Column(db.Integer, index=True, unique=True, nullable=False)
    security_label = db.Column(db.String(64), unique=False, nullable=True)
    code_smells = db.Column(db.Integer, index=True, unique=True, nullable=False)
    sqale_rating = db.Column(db.Integer, index=True, unique=True, nullable=False)
    sqale_label = db.Column(db.String(64), unique=False, nullable=True)
    alert_status = db.Column(db.String(64), unique=False, nullable=True)
    project = db.Column(db.String(64), unique=False, nullable=True)
    complexity = db.Column(db.Integer, index=True, unique=True, nullable=False)
    coverage = db.Column(db.Integer, index=True, unique=True, nullable=False)
    unit_tests = db.Column(db.String(64), unique=False, nullable=True)
    ncloc = db.Column(db.Integer, index=True, unique=True, nullable=False)
    duplicated_line_density = db.Column(
        db.Integer, index=True, unique=True, nullable=False
    )
    sqale_index = db.Column(db.Integer, index=True, unique=True, nullable=False)
    sqale_debt_ratio = db.Column(db.Integer, index=True, unique=True, nullable=False)
    size = db.Column(db.String(64), unique=False, nullable=True)
    dloc_label = db.Column(db.String(64), unique=False, nullable=True)
    coverage_label = db.Column(db.String(64), unique=False, nullable=True)
    quality_gate = db.Column(db.String(64), unique=False, nullable=True)

    def __repr__(self):
        return "<Metrica {}>".format(self.aplicacion)

    def to_dict(self):
        return {
                c.name: str(getattr(self, c.name)) for c in self.__table__.columns
            }
