import sqlite3

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
