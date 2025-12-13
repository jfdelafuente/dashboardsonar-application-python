from flask import render_template, request
from flask_login import login_required
from infocodest.home import home_bp

from datetime import datetime, date, timedelta

import infocodest.models.database as consulta
from infocodest.models.metricas import Metrica
from infocodest.models.stat import Stat
from infocodest.models.historico import Historico
from infocodest.models.proveedor import Proveedor
from infocodest.models.daily import Daily

from sqlalchemy.sql import func
from sqlalchemy import and_

# home_bp = Blueprint("home", __name__)


def get_distinct_apps():
    return Metrica.query.with_entities(Metrica.aplicacion).distinct().all()

def get_distinct_providers():
    return Proveedor.query.join(Metrica, Proveedor.aplicacion == Metrica.aplicacion).with_entities(Proveedor.proveedor).distinct().all()

def get_metricas():
    metricas = Metrica.query \
        .join(Proveedor, Proveedor.aplicacion == Metrica.aplicacion) \
        .order_by(Metrica.fecha.desc()) \
        .with_entities( Metrica.aplicacion,
                        Metrica.repo,
                        Metrica.size,
                        Metrica.fecha,
                        Metrica.reliability_label,
                        Metrica.reliability_rating,
                        Metrica.bugs,
                        Metrica.security_label,
                        Metrica.security_rating,
                        Metrica.vulnerabilities,
                        Metrica.sqale_label,
                        Metrica.sqale_rating,
                        Metrica.code_smells,
                        Metrica.alert_status,
                        Metrica.quality_gate,
                        Metrica.project,
                        Metrica.coverage,
                        Metrica.unit_tests,
                        Proveedor.tipo
                    ) \
        .all()
    return metricas


def get_stats():
    stats = Stat.query \
        .join(Proveedor, Proveedor.aplicacion == Stat.aplicacion) \
        .with_entities( Stat.aplicacion,
                        Stat.repos,
                        Stat.reliability_label,
                        Stat.reliability_rating,
                        Stat.security_label,
                        Stat.security_rating,
                        Stat.sqale_label,
                        Stat.sqale_rating,
                        Stat.alert_status_label,
                        Stat.alert_status_ok,
                        Stat.dloc_label,
                        Stat.dloc_rating,
                        Stat.coverage_label,
                        Stat.coverage_rating,
                        Proveedor.tipo
                    ) \
        .all()
    return stats


def get_metricas_aplicacion(project):
    return Metrica.query \
        .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
        .filter(Metrica.aplicacion == project) \
        .order_by(Metrica.fecha.desc()) \
        .with_entities( Metrica.aplicacion,
                        Metrica.repo,
                        Metrica.size,
                        Metrica.fecha,
                        Metrica.reliability_label,
                        Metrica.reliability_rating,
                        Metrica.bugs,
                        Metrica.security_label,
                        Metrica.security_rating,
                        Metrica.vulnerabilities,
                        Metrica.sqale_label,
                        Metrica.sqale_rating,
                        Metrica.code_smells,
                        Metrica.alert_status,
                        Metrica.quality_gate,
                        Metrica.project,
                        Metrica.coverage,
                        Metrica.unit_tests,
                        Proveedor.tipo
                    ) \
        .all()


def get_stats_aplicacion(project):
    return Stat.query \
        .join(Proveedor, Stat.aplicacion == Proveedor.aplicacion) \
        .filter(Stat.aplicacion == project) \
        .with_entities( Stat.aplicacion,
                        Stat.repos,
                        Stat.reliability_label,
                        Stat.reliability_rating,
                        Stat.security_label,
                        Stat.security_rating,
                        Stat.sqale_label,
                        Stat.sqale_rating,
                        Stat.alert_status_label,
                        Stat.alert_status_ok,
                        Stat.dloc_label,
                        Stat.dloc_rating,
                        Stat.coverage_label,
                        Stat.coverage_rating,
                        Proveedor.tipo
                    ) \
        .all()


def get_metricas_proveedor(project):
    return Metrica.query \
        .join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
        .filter(Proveedor.proveedor == project) \
        .order_by(Metrica.aplicacion.asc(), Metrica.fecha.desc()) \
        .with_entities( Metrica.aplicacion,
                        Metrica.repo,
                        Metrica.size,
                        Metrica.fecha,
                        Metrica.reliability_label,
                        Metrica.reliability_rating,
                        Metrica.bugs,
                        Metrica.security_label,
                        Metrica.security_rating,
                        Metrica.vulnerabilities,
                        Metrica.sqale_label,
                        Metrica.sqale_rating,
                        Metrica.code_smells,
                        Metrica.alert_status,
                        Metrica.quality_gate,
                        Metrica.project,
                        Metrica.coverage,
                        Metrica.unit_tests,
                        Proveedor.tipo
                    )


def get_stats_proveedor(project):
    return Stat.query \
        .join(Proveedor, Stat.aplicacion == Proveedor.aplicacion) \
        .filter(Proveedor.proveedor == project) \
        .with_entities( Stat.aplicacion,
                        Stat.repos,
                        # Stat.size,
                        # Stat.fecha,
                        Stat.reliability_label,
                        Stat.reliability_rating,
                        Stat.security_label,
                        Stat.security_rating,
                        Stat.sqale_label,
                        Stat.sqale_rating,
                        Stat.alert_status_label,
                        Stat.alert_status_ok,
                        Stat.dloc_label,
                        Stat.dloc_rating,
                        Stat.coverage_label,
                        Stat.coverage_rating,
                        Proveedor.tipo
                    ) \
        .all()


def get_dailys():
    return Daily.query.filter(Daily.created_on == date.today()-timedelta(days=1)).group_by(Daily.aplicacion) \
        .with_entities( Daily.aplicacion,
                        func.count('*').label('repo'),
                        Daily.proveedor,
                        Daily.created_on,
                        func.sum(Daily.num_bugs).label('num_bugs'),
                        func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                        func.sum(Daily.num_code_smells).label('num_code_smells'),
                        func.sum(Daily.num_quality).label('num_quality'),
                        func.sum(Daily.num_analisis).label('num_analisis')
                    ) \
        .all()


def get_dailys_proveedor(proveedor):
    return Daily.query.filter(Daily.created_on == date.today()-timedelta(days=1)).group_by(Daily.aplicacion) \
        .filter(Daily.proveedor == proveedor) \
        .with_entities( Daily.aplicacion,
                        func.count('*').label('repo'),
                        Daily.proveedor,
                        Daily.created_on,
                        func.sum(Daily.num_bugs).label('num_bugs'),
                        func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                        func.sum(Daily.num_code_smells).label('num_code_smells'),
                        func.sum(Daily.num_quality).label('num_quality'),
                        func.sum(Daily.num_analisis).label('num_analisis')
                    ) \
        .all()


def get_dailys_details_aplicacion(project):
    return Daily.query.filter(Daily.created_on == date.today()-timedelta(days=1)) \
        .filter(Daily.aplicacion == project) \
        .with_entities( Daily.aplicacion,
                        Daily.repo,
                        Daily.proveedor,
                        Daily.created_on,
                        Daily.num_bugs,
                        Daily.num_vulnerabilities,
                        Daily.num_code_smells,
                        Daily.num_quality,
                        Daily.num_analisis
                    ) \
        .all()


def get_dailys_details_repo(aplicacion, repo):
    return Daily.query.filter(Daily.created_on == date.today()-timedelta(days=1)) \
        .filter(and_(Daily.repo==repo, Daily.aplicacion==aplicacion)) \
        .with_entities( Daily.aplicacion,
                        Daily.repo,
                        Daily.proveedor,
                        Daily.created_on,
                        Daily.num_bugs,
                        Daily.num_vulnerabilities,
                        Daily.num_code_smells,
                        Daily.num_quality,
                        Daily.num_analisis
                    ) \
        .all()


def get_historico_name(project, name):
    return Historico.query \
        .join(Proveedor, Historico.aplicacion == Proveedor.aplicacion) \
        .filter(and_(Historico.repo == name, Historico.aplicacion== project)) \
        .order_by(Historico.fecha.desc()) \
        .with_entities( Historico.aplicacion,
                        Historico.repo,
                        Historico.size,
                        Historico.fecha,
                        Historico.reliability_label,
                        Historico.reliability_rating,
                        Historico.bugs,
                        Historico.security_label,
                        Historico.security_rating,
                        Historico.vulnerabilities,
                        Historico.sqale_label,
                        Historico.sqale_rating,
                        Historico.code_smells,
                        Historico.alert_status,
                        Historico.quality_gate,
                        Historico.project,
                        Historico.coverage,
                        Historico.unit_tests,
                        Proveedor.tipo
                    ) \
        .all()


@home_bp.route("/")
@login_required
def home():
    return render_template("home/index.html", 
                            date=datetime.now(), 
                            dato=consulta.getDatosMetricas())


@home_bp.route("/metricas")
@login_required
def metricas():
    # metricas = Metrica.query.all()
    return render_template("home/metricas/metricas.html", 
                            scores=get_metricas(), 
                            dato=consulta.getDatosMetricas())


@home_bp.route("/metricas/aplicacion", methods=("GET", "POST"))
@login_required
def historico():
    apps = get_distinct_apps()
    if request.method == "POST":
        project = request.form["project_name"]
        # print(f'Proyect name {project}')
        return render_template(
            "home/metricas/historico.html",
            apps=apps,
            scores=get_metricas_aplicacion(project),
            project=project,
            dato=consulta.getDatosAplicacion(project),
            success=True
        )
    else:
        return render_template("home/metricas/historico.html", apps=apps)


@home_bp.route("/metricas/proveedores", methods=("GET", "POST"))
@login_required
def proveedores():
    apps = get_distinct_providers()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/metricas/proveedores.html",
            apps=apps,
            scores = get_metricas_proveedor(project),
            proveedor=project,
            dato=consulta.getDatosProveedor(project),
            success=True
        )
    else:
        return render_template("home/metricas/proveedores.html", apps=apps)


@home_bp.route("/kpis")
@login_required
def kpis():
    kpis = Metrica.query.all()
    return render_template("home/kpis/kpis.html", scores=kpis, dato=consulta.getDatosMetricas())


@home_bp.route("/kpis/proveedores", methods=("GET", "POST"))
@login_required
def kpis_proveedores():
    apps = get_distinct_providers()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/kpis/kpis_proveedores.html",
            apps=apps,
            scores = Metrica.query.join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
                .filter(Proveedor.proveedor == project) \
                .order_by(Metrica.aplicacion.desc()),
            proveedor=project,
            dato=consulta.getDatosProveedor(project),
            success=True
        )
    else:
        return render_template("home/kpis/kpis_proveedores.html", apps=apps)


@home_bp.route("/kpis/aplicacion", methods=("GET", "POST"))
@login_required
def kpis_historico():
    apps = get_distinct_apps()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/kpis/kpis_historico.html",
            apps=apps,
            scores=get_metricas_aplicacion(project),
            date=datetime.now(),
            proveedor=project,
            dato=consulta.getDatosAplicacion(project),
            success=True
        )
    else:
        return render_template("home/kpis/kpis_historico.html", apps=apps)


@home_bp.route("/stats")
@login_required
def stats():
    return render_template("home/stats/stats.html", scores=get_stats(), dato=consulta.getDatosMetricas())


@home_bp.route("/stats/proveedores", methods=("GET", "POST"))
@login_required
def stats_proveedores():
    apps = get_distinct_providers()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/stats/stats_proveedores.html",
            apps=apps,
            scores = get_stats_proveedor(project),
            proveedor=project,
            dato=consulta.getDatosProveedor(project),
            success=True
        )
    else:
        return render_template("home/stats/stats_proveedores.html", apps=apps)


@home_bp.route("/metricas/aplicacion/<project>", methods=['GET', 'POST'])
def show_historico_project(project):
    apps = get_distinct_apps()
    return render_template(
        "home/metricas/historico.html",
        apps=apps,
        scores=get_metricas_aplicacion(project),
        project=project,
        dato=consulta.getDatosAplicacion(project),
        success=True
    )


@home_bp.route("/metricas/aplicacion/<project>/<name>", methods=['GET', 'POST'])
def show_historico_name(project, name):
    # apps = get_distinct_apps()
    return render_template(
        "home/metricas/charts_historico.html",
        # apps=apps,
        scores=get_historico_name(project, name),
        project=project,
        date=datetime.now(),
        name=name,
        success=True
    )


@home_bp.route("/kpis/aplicacion/<project>")
def show_kpis_historico_project(project):
    apps = get_distinct_apps()
    return render_template(
        "home/kpis/kpis_historico.html",
        apps=apps,
        scores=get_metricas_aplicacion(project),
        project=project,
        date=datetime.now(),
        dato=consulta.getDatosAplicacion(project),
        success=True
    )


@home_bp.route("/kpis/aplicacion/<project>/<name>")
def show_kpis_historico_name(project, name):
    apps = get_distinct_apps()
    return render_template(
        "home/kpis/kpis_charts_historico.html",
        apps=apps,
        scores=get_historico_name(project, name),
        name=name,
        date=datetime.now(),
        project=project,
        # dato=consulta.getDatosName(name),
        success=True
    )


@home_bp.route("/stats/aplicacion", methods=("GET", "POST"))
@login_required
def stats_historico():
    apps = get_distinct_apps()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/stats/stats_historico.html",
            apps=apps,
            scores=get_stats_aplicacion(project),
            proveedor=project,
            dato=consulta.getDatosAplicacion(project),
            success=True
        )
    else:
        return render_template("home/stats/stats_historico.html", apps=apps)


# peticion a moodificar para extraer las stats de cada repo del <project>
@home_bp.route("/stats/aplicacion/<project>", methods=("GET", "POST"))
def show_stats_historico_project(project):
    apps = get_distinct_apps()
    return render_template(
        "home/stats/stats_historico.html",
        apps=apps,
        scores=get_stats_aplicacion(project),
        proveedor=project,
        dato=consulta.getDatosAplicacion(project),
        success=True
    )


@home_bp.route("/dailys")
def dailys():
    return render_template("home/dailys/dailys.html", 
                            scores=get_dailys(), 
                            dato=consulta.getDatosMetricas())


@home_bp.route("/dailys/proveedores", methods=("GET", "POST"))
def dailys_proveedores():
    apps = get_distinct_providers()
    if request.method == "POST":
        project = request.form["project_name"]
        print(project)
        return render_template(
            "home/dailys/dailys_proveedores_chart.html",
            apps=apps,
            date=datetime.now(),
            scores = get_dailys_proveedor(project),
            project=project,
            dato=consulta.getDatosProveedor(project),
            success=True
        )
    else:
        return render_template("home/dailys/dailys_proveedores.html", apps=apps)


@home_bp.route("/dailys/aplicacion", methods=("GET", "POST"))
def dailys_historico():
    apps = get_distinct_apps()
    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/dailys/dailys_historico_chart.html",
            apps=apps,
            scores=get_dailys_details_aplicacion(project),
            project=project,
            date=datetime.now(),
            dato=consulta.getDatosAplicacion(project),
            success=True
        )
    else:
        return render_template("home/dailys/dailys_historico.html", apps=apps)


@home_bp.route("/dailys/aplicacion/<project>", methods=['GET', 'POST'])
def show_dailys_project(project):
    apps = get_distinct_apps()
    return render_template(
        "home/dailys/dailys_historico_chart.html",
        apps=apps,
        date=datetime.now(),
        scores=get_dailys_details_aplicacion(project),
        project=project,
        dato=consulta.getDatosAplicacion(project),
        success=True
    )


@home_bp.route("/dailys/aplicacion/<project>/<repo>", methods=['GET', 'POST'])
def show_dailys_repo(project, repo):
    apps = get_distinct_apps()
    return render_template(
        "home/dailys/dailys_historico_repo_chart.html",
        apps=apps,
        date=datetime.now(),
        scores=get_dailys_details_repo(project, repo),
        project=project,
        repo=repo,
        dato=consulta.getDatosRepositorios(project, repo),
        success=True
    )
