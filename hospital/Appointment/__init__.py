from pymongo import MongoClient

def get_db_connection():
    connection = MongoClient('localhost', 27017)
    db = connection.test_db
    return db

