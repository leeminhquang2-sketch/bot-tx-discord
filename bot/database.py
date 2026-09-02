# bot/database.py
import json
import os
from datetime import datetime, timedelta

DB_FILE = "data/database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "transactions": [], "settings": {}}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def get_user(user_id):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "balance": 0,
            "last_daily": None,
            "total_won": 0,
            "total_lost": 0,
            "games_played": 0,
            "username": "",
            "created_at": datetime.now().isoformat()
        }
        save_db(db)
    return db["users"][user_id]

def update_user(user_id, data):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "balance": 0,
            "last_daily": None,
            "total_won": 0,
            "total_lost": 0,
            "games_played": 0,
            "username": "",
            "created_at": datetime.now().isoformat()
        }
    db["users"][user_id].update(data)
    save_db(db)

def add_transaction(user_id, transaction_type, amount, details=""):
    db = load_db()
    db["transactions"].append({
        "user_id": str(user_id),
        "type": transaction_type,
        "amount": amount,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    save_db(db)

def get_all_users():
    db = load_db()
    return db["users"]

def get_transactions(limit=100):
    db = load_db()
    return db["transactions"][-limit:]

def get_user_transactions(user_id, limit=50):
    db = load_db()
    user_transactions = [t for t in db["transactions"] if t["user_id"] == str(user_id)]
    return user_transactions[-limit:]

def reset_database():
    confirm = input("⚠️ Bạn có chắc muốn reset database? (yes/no): ")
    if confirm.lower() == 'yes':
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        print("✅ Database đã được reset!")
        return True
    return False

def get_top_players(limit=10):
    users = get_all_users()
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('balance', 0), reverse=True)
    return sorted_users[:limit]
