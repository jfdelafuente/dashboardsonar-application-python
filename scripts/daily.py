import datetime
import os
import time
from database import Database
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

insert_into_stats = """ INSERT INTO daily (aplicacion, repo, proveedor, created_on, num_bugs, num_vulnerabilities, num_code_smells, num_quality, num_analisis)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) """


def create_schema(conn):
    with open("./scripts/sql/daily.sql") as f:
        conn.executescript(f.read())


def getDistinctAplicaciones(db):
    apps = db.cursor.execute("SELECT DISTINCT aplicacion FROM metricas").fetchall()
    data = [app[0] for app in apps]
    return data


def getDistinctRepoByAplicacion(db, app):
    names = db.cursor.execute(
        "SELECT repo FROM metricas where aplicacion=?", (app,)
    ).fetchall()
    data = [name[0] for name in names]
    return data


def getProveedor(db, app):
    query = "SELECT proveedor FROM PROVEEDOR \
        WHERE aplicacion='{}'".format(app)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getBugs(db, app, repo):
    query = "SELECT SUM(bugs)  \
            FROM METRICAS WHERE aplicacion = '{}' and repo ='{}'".format(app, repo)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getVul(db, app, repo):
    query = "SELECT SUM(vulnerabilities)  \
            FROM METRICAS WHERE aplicacion = '{}' and repo ='{}'".format(app, repo)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getCodeSmells(db, app, repo):
    query = "SELECT SUM(code_smells)  \
            FROM METRICAS WHERE aplicacion = '{}' and repo ='{}'".format(app, repo)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getAnalisis(db, app, repo):
    query = "SELECT count(repo)  \
            FROM Historico WHERE aplicacion = '{}' and repo ='{}'".format(app, repo)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getQuality(db, app, repo):
    query = "SELECT count(repo)  \
            FROM Historico WHERE aplicacion = '{}' and repo ='{}' and alert_status='{}'".format(app, repo, "OK")
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def extract_stats_from_db(db):
    project_ids = []
    apps = getDistinctAplicaciones(db)
    formato = "%Y-%m-%d"
    for app in apps:
        repos = getDistinctRepoByAplicacion(db, app)
        for repo in repos:
            start_date = datetime.datetime.now()  
            project_ids.append(
                (
                    app,
                    repo,
                    getProveedor(db, app), 
                    start_date.strftime(formato),
                    getBugs(db, app, repo),
                    getVul(db, app, repo),
                    getCodeSmells(db, app, repo),
                    getQuality(db, app, repo),
                    getAnalisis(db, app, repo),
                )
            )
    df_project = pd.DataFrame(
        project_ids,
        columns=[
            "aplicacion",
            "repos",
            "proveedor",
            "created_on",
            "num_bugs",
            "num_vulnerabilities",
            "num_code_smells",
            "num_quality",
            "num_analisis"
        ],
    )
    return df_project


def create_stats(db, df_stats):
    projects = []
    for i, measure in df_stats.iterrows():
        project = (
            measure["aplicacion"],
            measure["repos"],
            measure["proveedor"],
            measure["created_on"],
            int(measure["num_bugs"]),
            int(measure["num_vulnerabilities"]),
            int(measure["num_code_smells"]),
            int(measure["num_quality"]),
            int(measure["num_analisis"])
        )
        projects.append(project)
    number_of_rows = db.cursor.executemany(insert_into_stats, projects)
    db.connection.commit()
    print(f'>> Se han cargado {number_of_rows.rowcount} registros.')
    return df_stats


def main():
    database = r"" + os.environ["DATABASE"]
    with Database(database) as db:
        print("Proceso Daily iniciando ...")
        # print("Creando schema ...")
        # create_schema(db.connection)
        print("Extracción datos desde la BD ...")
        start_time = time.time()
        df_daily = extract_stats_from_db(db)
        print("Extracción Daily duration: {} seconds".format(time.time() - start_time))

        print("Cargando Daily en BD ...")
        start_time = time.time()
        df_daily = create_stats(db, df_daily)
        print("Carga Daily duration: {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()
