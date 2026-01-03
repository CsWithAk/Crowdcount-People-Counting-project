# auth/models.py
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# REPLACE WITH YOUR MONGODB ATLAS URI
MONGODB_URI = 'mongodb+srv://amit:amit@crowdcountdb.pjwxp4a.mongodb.net/' #'mongodb+srv://CrowdCountDB:Ak@123456@crowdcountdb.5dmmfrx.mongodb.net/' #"mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URI)
db = client['crowd_count_db']
users_collection = db['users']

def create_user(username, password, role="user"):
    if users_collection.find_one({"username": username}):
        return False, "User already exists"
    hashed = generate_password_hash(password)
    user_doc = {
        "username": username,
        "password": hashed,
        "role": role,  # 'admin' or 'user'
        "created_at": datetime.utcnow()
    }
    users_collection.insert_one(user_doc)
    return True, "User created"

def verify_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return {"username": user['username'], "role": user['role']}
    return None

def get_all_users():
    return list(users_collection.find({}, {"password": 0}))