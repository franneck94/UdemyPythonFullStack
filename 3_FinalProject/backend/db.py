import os

from pymongo import MongoClient


if "MONGODB_CONNECTION_STRING" in os.environ:
    MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]
    client = MongoClient(MONGODB_CONNECTION_STRING)
else:
    MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
    MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)

db = client["gw2tp_db"]
