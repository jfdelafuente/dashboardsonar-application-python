from flask import render_template, request
from flask_login import login_required
from infocodest.home import home_bp

from datetime import datetime

from infocodest.services import DashboardService

# home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@login_required
def home():
    dashboard_service = DashboardService()
    return render_template("home/index.html",
                          date=datetime.now(),
                          dato=dashboard_service.get_kpi_overview())


@home_bp.route("/metricas")
@login_required
def metricas():
    dashboard_service = DashboardService()
    return render_template("home/metricas/metricas.html",
                          scores=dashboard_service.get_all_metricas_with_proveedor(),
                          dato=dashboard_service.get_kpi_overview())


@home_bp.route("/metricas/aplicacion", methods=("GET", "POST"))
@login_required
def historico():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/metricas/historico.html",
            apps=apps,
            scores=dashboard_service.get_metricas_by_aplicacion(project),
            project=project,
            dato=dashboard_service.get_kpi_by_application(project),
            success=True
        )
    else:
        return render_template("home/metricas/historico.html", apps=apps)


@home_bp.route("/metricas/proveedores", methods=("GET", "POST"))
@login_required
def proveedores():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_providers()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/metricas/proveedores.html",
            apps=apps,
            scores=dashboard_service.get_metricas_by_proveedor(project),
            proveedor=project,
            dato=dashboard_service.get_kpi_by_proveedor(project),
            success=True
        )
    else:
        return render_template("home/metricas/proveedores.html", apps=apps)


@home_bp.route("/kpis")
@login_required
def kpis():
    dashboard_service = DashboardService()
    from infocodest.models.metricas import Metrica
    kpis = Metrica.query.all()
    return render_template("home/kpis/kpis.html",
                          scores=kpis,
                          dato=dashboard_service.get_kpi_overview())


@home_bp.route("/kpis/proveedores", methods=("GET", "POST"))
@login_required
def kpis_proveedores():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_providers()

    if request.method == "POST":
        project = request.form["project_name"]
        from infocodest.models.metricas import Metrica
        from infocodest.models.proveedor import Proveedor
        return render_template(
            "home/kpis/kpis_proveedores.html",
            apps=apps,
            scores=Metrica.query.join(Proveedor, Metrica.aplicacion == Proveedor.aplicacion) \
                .filter(Proveedor.proveedor == project) \
                .order_by(Metrica.aplicacion.desc()),
            proveedor=project,
            dato=dashboard_service.get_kpi_by_proveedor(project),
            success=True
        )
    else:
        return render_template("home/kpis/kpis_proveedores.html", apps=apps)


@home_bp.route("/kpis/aplicacion", methods=("GET", "POST"))
@login_required
def kpis_historico():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/kpis/kpis_historico.html",
            apps=apps,
            scores=dashboard_service.get_metricas_by_aplicacion(project),
            date=datetime.now(),
            proveedor=project,
            dato=dashboard_service.get_kpi_by_application(project),
            success=True
        )
    else:
        return render_template("home/kpis/kpis_historico.html", apps=apps)


@home_bp.route("/stats")
@login_required
def stats():
    dashboard_service = DashboardService()
    return render_template("home/stats/stats.html",
                          scores=dashboard_service.get_all_stats_with_proveedor(),
                          dato=dashboard_service.get_kpi_overview())


@home_bp.route("/stats/proveedores", methods=("GET", "POST"))
@login_required
def stats_proveedores():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_providers()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/stats/stats_proveedores.html",
            apps=apps,
            scores=dashboard_service.get_stats_by_proveedor(project),
            proveedor=project,
            dato=dashboard_service.get_kpi_by_proveedor(project),
            success=True
        )
    else:
        return render_template("home/stats/stats_proveedores.html", apps=apps)


@home_bp.route("/metricas/aplicacion/<project>", methods=['GET', 'POST'])
def show_historico_project(project):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/metricas/historico.html",
        apps=apps,
        scores=dashboard_service.get_metricas_by_aplicacion(project),
        project=project,
        dato=dashboard_service.get_kpi_by_application(project),
        success=True
    )


@home_bp.route("/metricas/aplicacion/<project>/<name>", methods=['GET', 'POST'])
def show_historico_name(project, name):
    dashboard_service = DashboardService()
    return render_template(
        "home/metricas/charts_historico.html",
        scores=dashboard_service.get_historico_by_aplicacion_and_repo(project, name),
        project=project,
        date=datetime.now(),
        name=name,
        success=True
    )


@home_bp.route("/kpis/aplicacion/<project>")
def show_kpis_historico_project(project):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/kpis/kpis_historico.html",
        apps=apps,
        scores=dashboard_service.get_metricas_by_aplicacion(project),
        project=project,
        date=datetime.now(),
        dato=dashboard_service.get_kpi_by_application(project),
        success=True
    )


@home_bp.route("/kpis/aplicacion/<project>/<name>")
def show_kpis_historico_name(project, name):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/kpis/kpis_charts_historico.html",
        apps=apps,
        scores=dashboard_service.get_historico_by_aplicacion_and_repo(project, name),
        name=name,
        date=datetime.now(),
        project=project,
        success=True
    )


@home_bp.route("/stats/aplicacion", methods=("GET", "POST"))
@login_required
def stats_historico():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/stats/stats_historico.html",
            apps=apps,
            scores=dashboard_service.get_stats_by_aplicacion(project),
            proveedor=project,
            dato=dashboard_service.get_kpi_by_application(project),
            success=True
        )
    else:
        return render_template("home/stats/stats_historico.html", apps=apps)


@home_bp.route("/stats/aplicacion/<project>", methods=("GET", "POST"))
def show_stats_historico_project(project):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/stats/stats_historico.html",
        apps=apps,
        scores=dashboard_service.get_stats_by_aplicacion(project),
        proveedor=project,
        dato=dashboard_service.get_kpi_by_application(project),
        success=True
    )


@home_bp.route("/dailys")
def dailys():
    dashboard_service = DashboardService()
    return render_template("home/dailys/dailys.html",
                          scores=dashboard_service.get_daily_summary(),
                          dato=dashboard_service.get_kpi_overview())


@home_bp.route("/dailys/proveedores", methods=("GET", "POST"))
def dailys_proveedores():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_providers()

    if request.method == "POST":
        project = request.form["project_name"]
        print(project)
        return render_template(
            "home/dailys/dailys_proveedores_chart.html",
            apps=apps,
            date=datetime.now(),
            scores=dashboard_service.get_daily_by_proveedor(project),
            project=project,
            dato=dashboard_service.get_kpi_by_proveedor(project),
            success=True
        )
    else:
        return render_template("home/dailys/dailys_proveedores.html", apps=apps)


@home_bp.route("/dailys/aplicacion", methods=("GET", "POST"))
def dailys_historico():
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()

    if request.method == "POST":
        project = request.form["project_name"]
        return render_template(
            "home/dailys/dailys_historico_chart.html",
            apps=apps,
            scores=dashboard_service.get_daily_details_by_aplicacion(project),
            project=project,
            date=datetime.now(),
            dato=dashboard_service.get_kpi_by_application(project),
            success=True
        )
    else:
        return render_template("home/dailys/dailys_historico.html", apps=apps)


@home_bp.route("/dailys/aplicacion/<project>", methods=['GET', 'POST'])
def show_dailys_project(project):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/dailys/dailys_historico_chart.html",
        apps=apps,
        date=datetime.now(),
        scores=dashboard_service.get_daily_details_by_aplicacion(project),
        project=project,
        dato=dashboard_service.get_kpi_by_application(project),
        success=True
    )


@home_bp.route("/dailys/aplicacion/<project>/<repo>", methods=['GET', 'POST'])
def show_dailys_repo(project, repo):
    dashboard_service = DashboardService()
    apps = dashboard_service.get_distinct_applications()
    return render_template(
        "home/dailys/dailys_historico_repo_chart.html",
        apps=apps,
        date=datetime.now(),
        scores=dashboard_service.get_daily_details_by_repo(project, repo),
        project=project,
        repo=repo,
        dato=dashboard_service.get_kpi_by_repository(project, repo),
        success=True
    )
