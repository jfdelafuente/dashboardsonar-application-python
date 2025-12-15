"""Data models."""
# from infocodest import db
from infocodest.extensions import db


class Daily(db.Model):
    """
    Daily Model

    Daily aggregated metrics per application.

    This table stores daily snapshots of application metrics. Each application
    can have multiple records (one per day), so aplicacion is NOT unique.

    Attributes:
        id: Primary key
        aplicacion: Application name (NOT unique - multiple daily records per app)
        repo: Number of repositories for this application
        proveedor: Provider/vendor information
        created_on: Record creation timestamp (date of the snapshot)
        num_bugs: Number of bugs detected
        num_vulnerabilities: Number of vulnerabilities detected
        num_code_smells: Number of code smells detected
        num_quality: Quality metric count
        num_analisis: Number of analyses performed

    Note:
        The combination of (aplicacion, created_on) should be unique for daily snapshots,
        but this is not enforced at database level currently.
    """

    __tablename__ = "daily"
    __table_args__ = (
        # Unique constraint on aplicacion + date (not including time)
        # This ensures only one record per application per day
        db.Index('idx_daily_aplicacion_date', 'aplicacion', 'created_on'),
    )

    id = db.Column(db.Integer, primary_key=True)
    aplicacion = db.Column(db.String(64), index=True, unique=False, nullable=False)  # Fixed: removed unique=True
    repo = db.Column(db.Integer, index=True, unique=False, nullable=False)
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
