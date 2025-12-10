from flask import jsonify, url_for, redirect, json, request
from infocodest.api import api_bp
from infocodest.models.metricas import Metrica
from infocodest.models.historico import Historico
from infocodest.models.registros import Registro
from infocodest.models.daily import Daily
from sqlalchemy.sql import func
from datetime import date, timedelta, datetime


@api_bp.route("/api/aplicacion/<aplicacion>")
def historico_project(aplicacion):
    data = {}
    metricas = Metrica.query.filter(Metrica.aplicacion == aplicacion).order_by(Metrica.fecha.asc()).all()
    data["project_name"] = [row.repo for row in metricas]
    data["aplicacion"] = [row.aplicacion for row in metricas]
    data["fecha"] = [row.fecha for row in metricas]
    data["bugs"] = [row.bugs for row in metricas]
    data["vulnerabilities"] = [row.vulnerabilities for row in metricas]
    data["codesmells"] = [row.code_smells for row in metricas]
    return jsonify(data)


@api_bp.route("/api/aplicacion/<project>/<name>")
def historico_name(project, name):
    data = {}
    scores = Historico.query.filter(Historico.repo == name, Historico.aplicacion == project) \
        .order_by(Historico.fecha.asc()).all()
    data["project_name"] = [row.repo for row in scores]
    data["aplicacion"] = [row.aplicacion for row in scores]
    data["fecha"] = [row.fecha for row in scores]
    data["bugs"] = [row.bugs for row in scores]
    data["vulnerabilities"] = [row.vulnerabilities for row in scores]
    data["codesmells"] = [row.code_smells for row in scores]
    return jsonify(data)


@api_bp.route("/api/registro")
def registro():
    limite = request.args.get('limit')
    valor = int(limite)
    fecha_actualizada = datetime.now() - timedelta(days=valor)
    return json.dumps([registro.to_dict() for registro in Registro.query.filter(Registro.created_on >= date(year=fecha_actualizada.year, month=fecha_actualizada.month, day=fecha_actualizada.day))])


@api_bp.route("/api/kpis")
def kpis():
    return json.dumps([registro.to_dict() for registro in Metrica.query.all()])


@api_bp.route("/api/kpis/<project>/<name>")
def kpis_historico_name(project, name):
    data = {}
    scores = Historico.query.filter(Historico.repo == name, Historico.aplicacion == project) \
        .order_by(Historico.fecha.asc()).all()
    data["project_name"] = [row.repo for row in scores]
    data["aplicacion"] = [row.aplicacion for row in scores]
    data["fecha"] = [row.fecha for row in scores]
    data["sqale_debt_ratio"] = [row.sqale_debt_ratio for row in scores]
    data["complexity"] = [row.complexity for row in scores]
    data["duplicated_line_density"] = [row.duplicated_line_density for row in scores]
    data["coverage"] = [row.coverage for row in scores]
    data["ncloc"] = [row.ncloc for row in scores]
    return jsonify(data)


@api_bp.route("/api/rating/<project>/<name>")
def rating_historico_name(project, name):
    data = {}
    scores = Metrica.query.filter(Metrica.repo == name, Metrica.aplicacion == project) \
        .order_by(Metrica.fecha.asc()).all()
    data["project_name"] = [row.repo for row in scores]
    data["aplicacion"] = [row.aplicacion for row in scores]
    data["fecha"] = [row.fecha for row in scores]
    data["sqale_rating"] = [row.sqale_rating for row in scores]
    data["reliability_rating"] = [row.reliability_rating for row in scores]
    data["security_rating"] = [row.security_rating for row in scores]
    return jsonify(data)


@api_bp.route("/api/daily/<aplicacion>")
def daily_aplicacion(aplicacion):
    data = {}
    dailys = Daily.query.filter(Daily.aplicacion == aplicacion) \
        .group_by(Daily.created_on) \
        .order_by(Daily.created_on.asc()) \
        .with_entities( Daily.aplicacion,
                        Daily.repo,
                        Daily.created_on,
                        func.sum(Daily.num_bugs).label('num_bugs'),
                        func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                        func.sum(Daily.num_code_smells).label('num_code_smells'),
                        func.sum(Daily.num_analisis).label('num_analisis')
                    ) \
        .all()
    data["project_name"] = [row.repo for row in dailys]
    data["aplicacion"] = [row.aplicacion for row in dailys]
    formato = "%Y-%m-%d"
    data['fecha'] = [row.created_on.strftime(formato) for row in dailys]
    data["bugs"] = [row.num_bugs for row in dailys]
    data["vulnerabilities"] = [row.num_vulnerabilities for row in dailys]
    data["codesmells"] = [row.num_code_smells for row in dailys]
    data["analisis"] = [row.num_analisis for row in dailys]
    return jsonify(data)

# prueba. no funciona
@api_bp.route("/api/daily/metrica/<aplicacion>")
def daily_aplicacion_metrica(aplicacion):
    metrica = request.args.get('metrica')
    campo = "Daily.num_{}".format(metrica)
    print(f'{campo}')
    data = {}
    dailys = Daily.query.filter_by(aplicacion=aplicacion) \
        .group_by(Daily.created_on) \
        .order_by(Daily.created_on.asc()) \
        .with_entities( Daily.aplicacion,
                        Daily.created_on,
                        func.sum(campo).label('metrica')
                    ) \
        .all()
    
    data["aplicacion"] = [row.aplicacion for row in dailys]
    data['fecha'] = [row.created_on.strftime("%Y-%m-%d") for row in dailys]
    data[metrica] = [row.metrica for row in dailys]
    return jsonify(data)


@api_bp.route("/api/daily/<aplicacion>/<repo>")
def daily_aplicacion_repo(aplicacion, repo):
    data = {}
    dailys = Daily.query.filter(Daily.repo == repo, Daily.aplicacion == aplicacion) \
        .group_by(Daily.created_on) \
        .order_by(Daily.created_on.asc()) \
        .with_entities( Daily.aplicacion,
                        Daily.repo,
                        Daily.created_on,
                        func.sum(Daily.num_bugs).label('num_bugs'),
                        func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                        func.sum(Daily.num_code_smells).label('num_code_smells'),
                        func.sum(Daily.num_analisis).label('num_analisis')
                    ) \
        .all()
    data['fecha'] = [row.created_on.strftime("%Y-%m-%d") for row in dailys]
    data["project_name"] = [row.repo for row in dailys]
    data["aplicacion"] = [row.aplicacion for row in dailys]
    data["bugs"] = [row.num_bugs for row in dailys]
    data["vulnerabilities"] = [row.num_vulnerabilities for row in dailys]
    data["codesmells"] = [row.num_code_smells for row in dailys]
    data["analisis"] = [row.num_analisis for row in dailys]
    return jsonify(data)


@api_bp.route("/api/daily/by_proveedor/<proveedor>")
def daily_proveedor(proveedor):
    
    dailys = Daily.query.filter(Daily.proveedor == proveedor) \
        .group_by(Daily.created_on) \
        .order_by(Daily.created_on.asc()) \
        .with_entities( Daily.proveedor,
                        Daily.created_on,
                        func.sum(Daily.num_bugs).label('num_bugs'),
                        func.sum(Daily.num_vulnerabilities).label('num_vulnerabilities'),
                        func.sum(Daily.num_code_smells).label('num_code_smells'),
                        func.sum(Daily.num_analisis).label('num_analisis')
                    ) \
        .all()
    data = {}
    data['fecha'] = [row.created_on.strftime("%Y-%m-%d") for row in dailys]
    data["proveedor"] = [row.proveedor for row in dailys]
    # data["fecha"] = [row.created_on for row in dailys]
    data["bugs"] = [row.num_bugs for row in dailys]
    data["vulnerabilities"] = [row.num_vulnerabilities for row in dailys]
    data["codesmells"] = [row.num_code_smells for row in dailys]
    data["analisis"] = [row.num_analisis for row in dailys]
    return jsonify(data)
