import os
import time
from utils.utils import extract_from_csv, load_to_csv
from database import Database
from dotenv import load_dotenv

load_dotenv()


insert_into_proveedor = """ INSERT INTO proveedor (aplicacion, proveedor, tipo) VALUES(?, ?, ?) """

proveedor_csv = "./datos/proveedores.csv"


def create_schema(conn):
    with open("./scripts/sql/proveedores.sql") as f:
        conn.executescript(f.read())



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


    with Database(database) as db:
        print("Creando schema ...")
        create_schema(db.connection)

        start_time = time.time()

        create_proveedor(db)
        print("Consulta Proveedor query duration: {} seconds".format(time.time() - start_time))
        

if __name__ == "__main__":
    main()
