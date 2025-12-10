from infocodest.charts import charts_bp
from infocodest.models.metricas import Metrica
from flask import render_template, request
from datetime import datetime
from infocodest.models.database import getRepositorios

@charts_bp.route("/")
def index():
    return render_template('charts/index.html', date=datetime.now())


@charts_bp.route("/charts_test")
def charts_test():
    scores = getRepositorios()
    labels = [row[0] for row in scores]
    values = [row[1] for row in scores]
    return render_template('charts/charts_test.html', labels=labels, values=values, date=datetime.now())


@charts_bp.route("/charts_historico", methods=('GET', 'POST'))
def charts_historico():
    apps = Metrica.query.with_entities(Metrica.aplicacion).distinct().all()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            'charts/charts_historico.html',
            apps=apps,
            date=datetime.now(),
            project=project,
            success=True
        )
    else:
        return render_template('charts/charts_historico.html', apps=apps, date=datetime.now())

@charts_bp.route("/charts_ejemplo")
def charts_ejemplo():
    return render_template('charts/charts_ejemplo.html', date=datetime.now())

@charts_bp.route("/charts_radar/<project>/<name>")
def charts_radar(project, name):
    return render_template('charts/charts_radar.html', 
                            project=project,
                            name=name,
                            date=datetime.now())
