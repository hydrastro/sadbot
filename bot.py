import requests
import json
import sqlite3

token = "placeholder"

base = "https://api.telegram.org/bot{}/".format(token)
con = sqlite3.connect('messages.db')

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

def get_previous_message_containing(message_info, string):
    chat_id = message_info["chat_id"]
    reply_to_id = message_info["reply_to_message_id"]
    cur = con.cursor()
    print(reply_to_id)
    if reply_to_id != None:
        cur.execute("SELECT * FROM messages WHERE Message LIKE ? and Message NOT LIKE 's/%' and ChatID = ? and MessageID = ? ORDER BY MessageID DESC",("%" + string + "%", chat_id, reply_to_id))
    else:
        cur.execute("SELECT * FROM messages WHERE Message LIKE ? and Message NOT LIKE 's/%' and ChatID = ? ORDER BY MessageID DESC",("%" + string + "%", chat_id))
    return cur.fetchone()

def get_reply(message_info):
    reply = None
    message = message_info["message"]
    print(message)
    if message is not None:
        if message.startswith("s/"):
            max_replace = 1
            if message.endswith("/"):
                message = message[:-1]
            if message.endswith("/g"):
                max_replace = len(message)
                message = message[:-2]
            split = message.split("/", 2)
            if len(split) != 3:
                return None
            old = split[1]
            new = split[2]
            print(old, new)
            if old != "" and new != "":
                reply_info = get_previous_message_containing(message_info, old)
                if reply_info != None:
                    reply = "<" + reply_info[1] + ">: "
                    reply += reply_info[4].replace(old, new, max_replace)
    return reply

def start_bot():
    update_id = None
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
                    reply = get_reply(current_message)
                    print(reply)
                    cur = con.cursor()
                    con.execute("INSERT INTO messages (MessageID, SenderName, SenderID, ChatID, Message, ReplyToMessageID) VALUES (?,?,?,?,?,?)", (message_id, sender_name, sender_id, chat_id, message, reply))
                    con.commit()
                    if reply != None:
                        con.execute("INSERT INTO messages (MessageID, SenderName, ChatID, Message) VALUES (?,?,?,?)", (0, "Real Human", chat_id, reply))
                        con.commit()
                        send_message(reply, chat_id)
start_bot()
