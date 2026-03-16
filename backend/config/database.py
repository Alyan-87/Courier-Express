from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "courier_express")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]

def get_db():
    return db