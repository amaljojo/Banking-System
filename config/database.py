
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PWD = os.getenv("MONGODB_PWD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PWD}@{MONGODB_HOST}/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client["Bank_demo"]
users_collection = db["users"] 
accounts_collection = db["accounts"]  
   