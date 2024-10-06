from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['dev-db']
languages = db['languages']
jokes = db['jokes']
articles = db['articles']

