import datetime
import os
from database import Database
from dotenv import load_dotenv

load_dotenv()

insert_into_stats = """ INSERT INTO registro (proceso, created_on, num_app, num_repo, num_bugs, num_quality, num_analisis)
                        VALUES(?, ?, ?, ?, ?, ?, ?) """

def create_schema(conn):
    with open("./scripts/sql/registro.sql") as f:
        conn.executescript(f.read())


def execute_query(db, query, params=None):
    return db.cursor.execute(query, params or {}).fetchone()


def getDatosMetricas(db):
    query = """
        SELECT
            COUNT(DISTINCT aplicacion) as num_app,
            COUNT(repo) as num_repo,
            SUM(bugs) as num_bugs
        FROM Metricas
    """
    
    query3 = """
        SELECT 
            COUNT(alert_status) as num_quality 
        FROM Historico 
        WHERE alert_status= :valor
    """
    
    query2 = """
        SELECT
            COUNT(*) as num_analisis
        FROM Historico
    """
    
    result = db.cursor.execute(query).fetchone()
    historico = db.cursor.execute(query2).fetchone()
    param = {'valor': "OK"}
    alert = db.cursor.execute(query3, param).fetchone()
    
    datos = {
        'num_app': result[0],
        'num_repo': result[1],
        'num_bugs': result[2],
        'num_quality': alert[0],
        'num_analisis' : historico[0]
    }
    return datos


def create_stats(db):
    datos = getDatosMetricas(db)
    formato = "%Y-%m-%d"
    start_date = datetime.datetime.now()  
    project = (
            "Registro informe Sonnar", 
            start_date.strftime(formato),
            int(datos['num_app']),
            int(datos['num_repo']),
            int(datos['num_bugs']),
            int(datos['num_quality']),
            int(datos['num_analisis']),
    )
    db.cursor.execute(insert_into_stats, project)
    db.connection.commit()
    return True


def main():
    database = r"" + os.environ["DATABASE"]
    with Database(database) as db:
        # print("Creando schema ...")
        # create_schema(db.connection)
        print("Cargando datos ...")
        if not create_stats(db):
            print("Error Carga Registro")
        print("Fin Carga registro ...")


if __name__ == "__main__":
    main()
