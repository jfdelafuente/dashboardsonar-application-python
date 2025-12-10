import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

insert_into_stats = """ INSERT INTO stats (aplicacion, repos, reliability_rating, reliability_label, sqale_rating, sqale_label, security_rating, security_label,
                        alert_status_ok, alert_status_label, dloc_rating, dloc_label, coverage_rating, coverage_label)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

datos_csv = "./datos/stats.csv"


class Database:
    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"an error occurred: {exc_val}")
        self.connection.close()

def getDistinctAplicaciones(db):
    apps = db.cursor.execute("SELECT DISTINCT aplicacion FROM metricas").fetchall()
    data = [app[0] for app in apps]
    return data

def getHistorico(db):
    apps = db.cursor.execute("SELECT DISTINCT aplicacion FROM historico").fetchall()
    data = [app[0] for app in apps]
    return data

def getProveedor(db):
    apps = db.cursor.execute("SELECT DISTINCT proveedor FROM proveedor").fetchall()
    data = [app[0] for app in apps]
    return data 


def getUsuarios(db):
    apps = db.cursor.execute("SELECT username, password from users").fetchall()
    data = [app[0] for app in apps]
    return data 


def main():
    database = r"" + os.environ["DATABASE"]
    with Database(database) as db:
        print("Provando schema ...")
        data = getDistinctAplicaciones(db)
        print(f"Metricas : {len(data)}")
        indice = 0
        while indice < len(data):
            print(data[indice])
            indice+=1
            
            
        data = getHistorico(db)
        print(f"Historicos : {len(data)}")
        indice = 0
        while indice < len(data):
            print(data[indice])
            indice+=1


        data = getProveedor(db)
        print(f"Proveedores : {len(data)}")
        indice = 0
        while indice < len(data):
            print(data[indice])
            indice+=1
            
        data = getUsuarios(db)
        print(f"Usuarios : {len(data)}")
        indice = 0
        while indice < len(data):
            print(data[indice])
            indice+=1

if __name__ == "__main__":
    main()
