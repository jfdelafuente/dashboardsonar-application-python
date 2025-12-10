import os
import time
from utils.utils import extract_from_csv, load_to_csv
from etl.etl import transformar_historico, transformar_metricas
from database import Database
from dotenv import load_dotenv

load_dotenv()

insert_into_metricas = """ INSERT INTO metricas   (repo, aplicacion, fecha, bugs, reliability_rating, reliability_label,
                        vulnerabilities, security_rating, security_label, code_smells, sqale_rating, sqale_label,
                        alert_status, project, complexity, coverage, unit_tests, ncloc, duplicated_line_density, sqale_index,
                        sqale_debt_ratio, size, dloc_label, coverage_label, quality_gate)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?) """

insert_into_historico = """ INSERT INTO historico (repo, aplicacion, fecha, bugs, reliability_rating, reliability_label,
                        vulnerabilities, security_rating, security_label, code_smells, sqale_rating, sqale_label,
                        alert_status, project, complexity, coverage, unit_tests, ncloc, duplicated_line_density, sqale_index,
                        sqale_debt_ratio, size, dloc_label, coverage_label, quality_gate)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?) """

insert_into_proveedor = """ INSERT INTO proveedor (aplicacion, proveedor, tipo) VALUES(?, ?, ?) """

# datos_csv = "./datos/metricas.csv"
# historico_csv = "./datos/historico.csv"
proveedor_csv = "./datos/proveedores.csv"


def create_schema(conn):
    with open("./scripts/sql/schema.sql") as f:
        conn.executescript(f.read())


def create_metricas(db, df_measures):
    print("Extract datos metricas csv ...")
    projects = []
    for i, measure in df_measures.iterrows():
        project = (
            measure["name"] + "-" + measure["tipo"] + "-" + measure["lenguaje"],
            measure["aplicacion"],
            measure["date"],
            int(measure["bugs"]),
            int(measure["reliability_rating"]),
            measure["reliability_label"],
            int(measure["vulnerabilities"]),
            int(measure["security_rating"]),
            measure["security_label"],
            int(measure["code_smells"]),
            int(measure["sqale_rating"]),
            measure["sqale_label"],
            measure["alert_status"],
            measure["project"],
            int(measure["complexity"]),
            float(measure["coverage"]),
            'N/A',
            int(measure["ncloc"]),
            float(measure["duplicated_lines_density"]),
            int(measure["sqale_index"]),
            float(measure["sqale_debt_ratio"]),
            measure["size"],
            measure["dloc_label"],
            measure["coverage_label"],
            measure["quality_gate"],
        )
        projects.append(project)
        
    number_of_rows = db.cursor.executemany(insert_into_metricas, projects)
    db.connection.commit()
    print(number_of_rows.rowcount)


def create_historico(db, df_measures):
    print("Extract datos historico csv ...")
    projects = []
    for i, measure in df_measures.iterrows():
        project = (
            measure["name"] + "-" + measure["tipo"] + "-" + measure["lenguaje"],
            measure["aplicacion"],
            measure["date"],
            int(measure["bugs"]),
            int(measure["reliability_rating"]),
            measure["reliability_label"],
            int(measure["vulnerabilities"]),
            int(measure["security_rating"]),
            measure["security_label"],
            int(measure["code_smells"]),
            int(measure["sqale_rating"]),
            measure["sqale_label"],
            measure["alert_status"],
            measure["project"],
            int(measure["complexity"]),
            float(measure["coverage"]),
            'N/A',
            int(measure["ncloc"]),
            float(measure["duplicated_lines_density"]),
            int(measure["sqale_index"]),
            float(measure["sqale_debt_ratio"]),
            measure["size"],
            measure["dloc_label"],
            measure["coverage_label"],
            measure["quality_gate"]
        )
        projects.append(project)

    number_of_rows = db.cursor.executemany(insert_into_historico, projects)
    db.connection.commit()
    print(number_of_rows.rowcount)


def create_proveedor(db):
    print("Extract datos proveedor csv ...")
    df_measures = extract_from_csv(proveedor_csv)
    for i, measure in df_measures.iterrows():
        project = (measure["aplicacion"], measure["proveedor"], measure["tipo"])
        db.cursor.execute(insert_into_proveedor, project)
        db.connection.commit()
    print(db.cursor.lastrowid)


def main():

    database = r"" + os.environ["DATABASE"]
    datos_in = r"" + os.environ["DATOS_CSV"]
    historico_in = r"" + os.environ["HISTORICO_CSV"]
    
    print("Transformamos los datos de metricas e historicos")
    data = transformar_metricas(datos_in)
    historico = transformar_historico(historico_in)
    
    # datos_csv = "./datos/metricas.csv"
    # historico_csv = "./datos/historico.csv"
    # print(f"Generamos fichero Métricas: {datos_csv}")
    # load_to_csv(datos_csv, data)
    # print(f"Generamos fichero Historico: {historico_csv}")
    # load_to_csv(historico_csv, historico)

    with Database(database) as db:
        print("Creando schema ...")
        create_schema(db.connection)
        print("Cargando datos ...")
        start_time = time.time()
        create_metricas(db, data)
        print("Consulta Metrica query duration: {} seconds".format(time.time() - start_time))
        create_historico(db, historico)
        print("Consulta Historico query duration: {} seconds".format(time.time() - start_time))
        create_proveedor(db)
        print("Consulta Proveedor query duration: {} seconds".format(time.time() - start_time))
        

if __name__ == "__main__":
    main()
