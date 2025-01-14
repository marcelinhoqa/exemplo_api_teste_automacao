from db import Db

def initialize_database():
    db = Db()
    db.create_tables()
    return db