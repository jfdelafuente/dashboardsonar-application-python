import os
import time
from database import Database
from utils.utils import load_to_csv
from etl.etl import transformar_stats
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

insert_into_stats = """ INSERT INTO stats (aplicacion, repos, reliability_rating, reliability_label, sqale_rating, sqale_label, security_rating, security_label,
                        alert_status_ok, alert_status_label, dloc_rating, dloc_label, coverage_rating, coverage_label)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

datos_csv = "./datos/stats.csv"


def create_schema(conn):
    with open("./scripts/sql/stats.sql") as f:
        conn.executescript(f.read())


def getDistinctAplicaciones(db):
    apps = db.cursor.execute("SELECT DISTINCT aplicacion FROM metricas").fetchall()
    data = [app[0] for app in apps]
    return data


def getDistinctRepoByAplicacion(db, app):
    names = db.cursor.execute(
        "SELECT name FROM metricas where aplicacion=?", (app,)
    ).fetchall()
    data = [name[0] for name in names]
    return data


def getNumRepobyAplicacion(db, app):
    query = "SELECT count(repo), aplicacion from metricas \
        WHERE aplicacion='{}' GROUP BY aplicacion".format(
        app
    )
    # print(query)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getLabelA(db, app, label):
    query = "SELECT count({}), aplicacion from metricas \
        WHERE aplicacion='{}' and {}='A' GROUP BY aplicacion".format(
        label, app, label
    )
    # print(query)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def getStatus(db, app, label):
    query = "SELECT count(alert_status), aplicacion from metricas \
        WHERE aplicacion='{}' and alert_status = '{}' GROUP BY aplicacion".format(
        app, label
    )
    # print(query)
    record = db.cursor.execute(query).fetchone()
    if record is None:
        return 0
    return record[0]


def extract_stats_from_db(db):
    project_ids = []
    apps = getDistinctAplicaciones(db)
    for app in apps:
        project_ids.append(
            (
                app,
                getNumRepobyAplicacion(db, app),
                getLabelA(db, app, "reliability_label"),
                getLabelA(db, app, "sqale_label"),
                getLabelA(db, app, "security_label"),
                getStatus(db, app, "OK"),
                getLabelA(db, app, "dloc_label"),
                getLabelA(db, app, "coverage_label"),
            )
        )
    df_project = pd.DataFrame(
        project_ids,
        columns=[
            "aplicacion",
            "repos",
            "reliability_rating",
            "sqale_rating",
            "security_rating",
            "alert_status_ok",
            "dloc_rating",
            "coverage_rating",
        ],
    )
    return df_project


def create_stats(db, df_stats):
    projects = []
    for i, measure in df_stats.iterrows():
        project = (
            measure["aplicacion"],
            int(measure["repos"]),
            int(measure["reliability_rating"]),
            measure["reliability_label"],
            int(measure["sqale_rating"]),
            measure["sqale_label"],
            int(measure["security_rating"]),
            measure["security_label"],
            int(measure["alert_status_ok"]),
            measure["alert_status_label"],
            int(measure["dloc_rating"]),
            measure["dloc_label"],
            int(measure["coverage_rating"]),
            measure["coverage_label"],
        )
        projects.append(project)
    number_of_rows = db.cursor.executemany(insert_into_stats, projects)
    db.connection.commit()
    print(number_of_rows.rowcount)
    return df_stats


def main():
    database = r"" + os.environ["DATABASE"]
    with Database(database) as db:
        print("Creando schema ...")
        create_schema(db.connection)
        df_stats = extract_stats_from_db(db)

        print("Transformando datos ...")
        df_stats = transformar_stats(df_stats)

        print("Cargando Stats en BD ...")
        start_time = time.time()
        df_stats = create_stats(db, df_stats)
        print("Consulta Stats query duration: {} seconds".format(time.time() - start_time))

        # print(f"Creando fichero datos: {datos_csv}")
        # load_to_csv(datos_csv, df_stats)


if __name__ == "__main__":
    main()
