import json

CHAT_LOG_FILE = "database/chat_log.json"

def save_message(username, message):
    chat_data = {username: message}
    with open(CHAT_LOG_FILE, "a") as file:
        json.dump(chat_data, file)
        file.write("\n")
