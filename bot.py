import requests
import json

token = ""
buffer_size = 1000

base = "https://api.telegram.org/bot{}/".format(token)

def get_updates(offset = None):
    url = base + "getUpdates?timeout=50"
    if offset:
        url = url + "&offset={}".format(offset + 1)
    r = requests.get(url)
    return json.loads(r.content)

def send_message(message, chat_id):
    url = base + "sendMessage?chat_id={}&text={}".format(chat_id, message)
    if message is not None:
        requests.get(url)

def get_previous_message_containing(database, message_info, string):
    chat_id = message_info["chat_id"]
    reply_to_id = message_info["reply_to_message_id"]
    print database
    print string
    for entry in reversed(database):
        print entry
        if string in entry["message"] and not entry["message"].startswith("s/") and entry["chat_id"] == chat_id and (reply_to_id == None or reply_to_id == entry["message_id"]):
            return entry
    return None

def get_reply(database, message_info):
    reply = None
    message = message_info["message"]
    if message is not None:
        if message.startswith("s/"):
            if message.endswith("/"):
                message = message[:-1]
            split = message.split("/", 2)
            if len(split) != 3:
                return None
            old = split[1]
            new = split[2]
            if old != "" and new != "":
                reply_info = get_previous_message_containing(database, message_info, old)
                if reply_info != None:
                    reply = "<" + reply_info["sender_name"] + ">: "
                    reply += reply_info["message"].replace(old, new)
    return reply

def start_bot():
    update_id = None
    database = []
    while True:
        updates = get_updates(offset = update_id)
        updates = updates["result"]
        if updates:
            for item in updates:
                update_id = item["update_id"]
                try:
                    message = str(item["message"]["text"])
                except:
                    message = None
                if message != None:
                    message_id = item["message"]["message_id"]
                    sender_name = item["message"]["from"]["first_name"]
                    sender_id = item["message"]["from"]["id"]
                    chat_id = item["message"]["chat"]["id"]
                    reply_to_message_id = None
                    if "reply_to_message" in item["message"]:
                        reply_to_message_id = item["message"]["reply_to_message"]["message_id"]
                    current_message = {"message_id": message_id, "sender_name": sender_name, "sender_id": sender_id, "chat_id": chat_id, "message": message, "reply_to_message_id": reply_to_message_id}
                    reply = get_reply(database, current_message)
                    database.append(current_message)
                    if reply != None:
                        reply_info = {"message_id": 0, "sender_name": "Real Human", "chat_id": chat_id, "message": reply}
                        database.append(reply_info)
                        send_message(reply, chat_id)
                    if len(database) > buffer_size:
                        database.pop(0)
start_bot()
