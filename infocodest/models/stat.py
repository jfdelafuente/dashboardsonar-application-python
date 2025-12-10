"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Stat(db.Model):
    """Data model for user accounts."""

    __tablename__ = "stats"

    id = db.Column(db.Integer, primary_key=True)
    aplicacion = db.Column(db.String(64), index=False, unique=True, nullable=False)
    repos = db.Column(db.Integer, index=True, unique=True, nullable=False)
    reliability_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    reliability_rating = db.Column(
        db.Integer, index=False, unique=False, nullable=False
    )
    sqale_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    sqale_rating = db.Column(db.Integer, index=False, unique=False, nullable=False)
    security_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    security_rating = db.Column(db.Integer, index=False, unique=False, nullable=False)
    alert_status_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    alert_status_ok = db.Column(db.Integer, index=False, unique=False, nullable=False)
    dloc_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    dloc_rating = db.Column(db.Integer, index=False, unique=False, nullable=False)
    coverage_label = db.Column(db.Text, index=False, unique=False, nullable=True)
    coverage_rating = db.Column(db.Integer, index=False, unique=False, nullable=False)

    def __repr__(self):
        return "<Stat {}>".format(self.aplicacion)
