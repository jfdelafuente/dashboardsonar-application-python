from sqlalchemy import create_engine, text
import os
import datetime
import json
from config import config

db_connection_string = r"sqlite:///" + os.environ['DATABASE']
# db_connection_string = r"sqlite:///db.sqlite3"
DAYS = int(os.environ['DAYS'])
# DAYS = 15

engine = create_engine(
    db_connection_string,
)


def definir_texto(v1, v2):
    if (v1==0) & (v2==0):
        avance = 0
        comparativa = "Igual"
    else:
        try:
            avance = (v1 / v2) * 100 - 100
        except ZeroDivisionError:
            print("Trataste de dividir entre cero :( ")
            avance = 100
        except Exception:
            print("Tipos no soportados")
            avance = 100
        comparativa = "Decrease" if avance < 0 else "Increase"
    return round(avance, 1), comparativa


def obtener_fecha_hace_dias(dias):
    start_date = datetime.datetime.now() - datetime.timedelta(dias)
    return start_date.strftime("%Y-%m-%d")


def ejecutar_consultas(conn, queries, params):
    results = {key: conn.execute(text(query), params).fetchone() for key, query in queries.items()}
    return {key: value[0] if value is not None else 0 for key, value in results.items()}


def calcular_datos(datos, old_datos, keys):
    resultados = {}
    for key in keys:
        resultados[f'{key}'] = datos[key]
        avance, comparativa = definir_texto(datos[key], old_datos[key])
        resultados[f'{key}_value'] = '{:.2f}'.format(avance)
        resultados[f'{key}_text'] = '{:.2f}% {} in {} Days'.format(avance, comparativa, DAYS)
    # print(json.dumps(resultados, indent=4))
    return resultados


def getDatosComunes(queries, params):
    with engine.connect() as conn:
        datos = ejecutar_consultas(conn, queries, params)
        return datos


def getDatosMetricas():
    fecha = obtener_fecha_hace_dias(DAYS)
    queries = {
        'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM Metricas",
        'repositorios': "SELECT COUNT(repo) FROM Metricas",
        'bugs': "SELECT SUM(bugs) FROM Metricas",
        'analisis': "SELECT COUNT(*) FROM Historico",
        'quality': "SELECT COUNT(alert_status) FROM Historico WHERE alert_status='OK'"
    }
    params = {}
    datos = getDatosComunes(queries, params)
    print(datos)
    
    queries = {
            'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM DAILY WHERE created_on= :fecha",
            'repositorios': "SELECT COUNT(repo) FROM DAILY WHERE created_on= :fecha",
            'bugs': "SELECT SUM(num_bugs) FROM DAILY WHERE created_on= :fecha",
            'analisis': "SELECT sum(num_analisis) FROM DAILY WHERE created_on= :fecha",
            'quality': "SELECT sum(num_quality) FROM DAILY WHERE created_on= :fecha",
        }
    old_params = {'fecha': fecha, **params}
    old_datos = getDatosComunes(queries, old_params)
    print(f'Obtener Valores de {fecha}')
    print(old_datos)
    
    return calcular_datos(datos, old_datos, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])


def getDatosAplicacion(project):
    fecha = obtener_fecha_hace_dias(DAYS)
    queries = {
        'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM Metricas WHERE aplicacion = :id",
        'repositorios': "SELECT COUNT(DISTINCT(repo)) FROM Metricas WHERE aplicacion = :id",
        'bugs': "SELECT SUM(bugs) FROM Metricas WHERE aplicacion = :id",
        'analisis': "SELECT COUNT(*) FROM Historico where aplicacion = :id",
        'quality': "SELECT COUNT(alert_status) FROM Historico WHERE alert_status='OK' AND aplicacion = :id"
    }
    params = {'id': project}
    datos = getDatosComunes(queries, params)
    print(datos)
    
    queries = {
            'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM DAILY WHERE created_on= :fecha AND aplicacion= :id",
            'repositorios': "SELECT COUNT(DISTINCT(repo)) FROM DAILY WHERE created_on= :fecha AND aplicacion= :id",
            'bugs': "SELECT SUM(num_bugs) FROM DAILY WHERE created_on= :fecha AND aplicacion= :id",
            'analisis': "SELECT sum(num_analisis) FROM DAILY WHERE created_on= :fecha AND aplicacion= :id",
            'quality': "SELECT sum(num_quality) FROM DAILY WHERE created_on= :fecha AND aplicacion= :id"
    }
    old_params = {'fecha': fecha, **params}
    old_datos = getDatosComunes(queries, old_params)
    print(old_datos)
    
    return calcular_datos(datos, old_datos, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])



def getDatosProveedor(proveedor):
    fecha = obtener_fecha_hace_dias(DAYS)
    queries = {
        'aplicaciones': "SELECT COUNT(DISTINCT(metricas.aplicacion)) FROM Metricas \
            INNER JOIN proveedor ON proveedor.aplicacion=metricas.aplicacion \
            WHERE proveedor.proveedor= :id",
        'repositorios': "SELECT COUNT(metricas.repo) FROM Metricas \
            INNER JOIN Proveedor ON proveedor.aplicacion=metricas.aplicacion \
            WHERE proveedor.proveedor= :id",
        'bugs': "SELECT SUM(metricas.bugs) FROM Metricas \
            INNER JOIN proveedor ON proveedor.aplicacion=metricas.aplicacion \
            WHERE proveedor.proveedor= :id",
        'analisis': "SELECT COUNT(*) FROM Historico \
            INNER JOIN proveedor ON proveedor.aplicacion=historico.aplicacion \
            WHERE proveedor.proveedor= :id",
        'quality': "SELECT COUNT(historico.alert_status) FROM Historico \
            INNER JOIN proveedor ON proveedor.aplicacion=historico.aplicacion \
            WHERE historico.alert_status='OK' AND proveedor.proveedor= :id"
    }
    params = {'id': proveedor}
    datos = getDatosComunes(queries, params)
    # print(f'getDatosProveedor')
    print(datos)
    
    queries = {
            'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM DAILY WHERE created_on= :fecha AND proveedor= :id",
            'repositorios': "SELECT COUNT(repo) FROM DAILY WHERE created_on= :fecha AND proveedor= :id",
            'bugs': "SELECT SUM(num_bugs) FROM DAILY WHERE created_on= :fecha AND proveedor= :id",
            'analisis': "SELECT sum(num_analisis) FROM DAILY WHERE created_on= :fecha AND proveedor= :id",
            'quality': "SELECT sum(num_quality) FROM DAILY WHERE created_on= :fecha AND proveedor= :id"
    }
    old_params = {'fecha': fecha, **params}
    old_datos = getDatosComunes(queries, old_params)
    print(old_datos)
    
    return calcular_datos(datos, old_datos, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])


def getRepositorios():
    query_repos = text(
        "SELECT aplicacion, COUNT(*) AS NUM_REPO "
        "FROM metricas "
        "GROUP BY aplicacion "
        "HAVING COUNT(*) > 2 "
        "ORDER BY COUNT(*) DESC;"
    )
    
    with engine.connect() as conn:
        repos = conn.execute(query_repos).fetchall()
    
    return repos


def getDatosRepositorios(project, repo):
    fecha = obtener_fecha_hace_dias(DAYS)
    queries = {
        'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM Metricas WHERE repo = :id AND aplicacion = :app",
        'repositorios': "SELECT COUNT(repo) FROM Metricas WHERE repo = :id AND aplicacion = :app",
        'bugs': "SELECT SUM(bugs) FROM Metricas WHERE repo = :id AND aplicacion = :app",
        'analisis': "SELECT COUNT(*) FROM Historico WHERE repo = :id AND aplicacion = :app",
        'quality': "SELECT COUNT(alert_status) FROM Historico WHERE alert_status='OK' AND repo = :id AND aplicacion = :app"
    }
    params = {'id': repo, 'app': project}
    datos = getDatosComunes(queries, params)
    print(datos)
    
    queries = {
            'aplicaciones': "SELECT COUNT(DISTINCT(aplicacion)) FROM DAILY WHERE created_on= :fecha AND repo= :id AND aplicacion = :app",
            'repositorios': "SELECT COUNT(repo) FROM DAILY WHERE created_on= :fecha AND repo= :id AND aplicacion = :app",
            'bugs': "SELECT SUM(num_bugs) FROM DAILY WHERE created_on= :fecha AND repo= :id AND aplicacion = :app",
            'analisis': "SELECT sum(num_analisis) FROM DAILY WHERE created_on= :fecha AND repo= :id AND aplicacion = :app",
            'quality': "SELECT num_quality FROM DAILY WHERE created_on= :fecha AND repo= :id AND aplicacion = :app"
    }
    old_params = {'fecha': fecha, **params}
    old_datos = getDatosComunes(queries, old_params)
    print(old_datos)
    
    return calcular_datos(datos, old_datos, ['aplicaciones', 'repositorios', 'bugs', 'analisis', 'quality'])