import json

def authenticate_user(username):
    with open("database/users.json", "r") as user_db:
        users = json.load(user_db)
    return username in users  # Checks if username exists
