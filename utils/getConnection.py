import sqlite3
import os

connection = None

def getConnection():
    global connection
    if connection is not None:
        return connection

    database_filepath = os.path.join("database", "database.sqlite")
    
    connection = sqlite3.connect(database_filepath)
    connection.row_factory = sqlite3.Row
    return connection