import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


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
        
    def commit(self):
        """commit changes to database"""
        self.connection.commit()


def getDistinctAplicaciones(db):
    apps = db.cursor.execute("SELECT id FROM registro ORDER BY id DESC").fetchone()
    return apps[0]

    
def updateDownFecha(db, id_registro, fecha_actual):
    contador = id_registro
    id = 1
    while contador > 0:
        fecha_actualizada = fecha_actual - timedelta(days=contador)
        formato1 = "%Y-%m-%d"
        fecha = fecha_actualizada.strftime(formato1) 
        print(fecha) 
        
        db.cursor.execute("UPDATE registro SET created_on = ? WHERE id = ?", (fecha, id))
        db.commit()
        id += 1
        contador -= 1


def main():
    database = r"" + os.environ["DATABASE"]
    with Database(database) as db:
        print("Provando schema ...")
        data = getDistinctAplicaciones(db)
        print(f'Valores: {data}')
        updateDownFecha(db, data, datetime.now())
            

if __name__ == "__main__":
    main()
