"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Stat(db.Model):
    """
    Statistics Model

    Aggregated statistics per application from metricas table.

    Attributes:
        id: Primary key
        aplicacion: Application name (unique)
        repos: Number of repositories for this application
        reliability_rating: Count of 'A' reliability ratings
        reliability_label: Aggregated reliability label
        sqale_rating: Count of 'A' sqale (maintainability) ratings
        sqale_label: Aggregated sqale label
        security_rating: Count of 'A' security ratings
        security_label: Aggregated security label
        alert_status_ok: Count of 'OK' quality gate status
        alert_status_label: Aggregated alert status label
        dloc_rating: Count of 'A' duplicated lines density ratings
        dloc_label: Aggregated dloc label
        coverage_rating: Count of 'A' coverage ratings
        coverage_label: Aggregated coverage label
    """

    __tablename__ = "stats"

    id = db.Column(db.Integer, primary_key=True)
    aplicacion = db.Column(db.String(64), index=False, unique=True, nullable=False)
    repos = db.Column(db.Integer, index=True, unique=False, nullable=False)  # Fixed: removed unique=True
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
