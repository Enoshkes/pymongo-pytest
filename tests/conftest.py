import pytest
from pymongo import MongoClient

@pytest.fixture(scope="module")
def db_connection():
    client = MongoClient('mongodb://localhost:27017')
    real_db = client['dev-db']
    test_db = client['dev-test-db']

    collections_to_copy = ['jokes', 'languages', 'articles']

    for collection_name in collections_to_copy:
        if collection_name in real_db.list_collection_names():
            test_db.drop_collection(collection_name)
            test_db[collection_name].insert_many(real_db[collection_name].find())

    yield test_db
    client.drop_database('dev-test-db')
    client.close()

@pytest.fixture(scope="module")
def jokes_collection(db_connection):
    collection = db_connection['jokes']
    return collection

@pytest.fixture(scope="module")
def languages_collection(db_connection):
    collection = db_connection['languages']
    return collection
 
@pytest.fixture(scope="module")
def articles_collection(db_connection):
    collection = db_connection['articles']
    return collection
 