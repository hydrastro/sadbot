import config
import json
import random
import re
import requests
import sqlite3

base = "https://api.telegram.org/bot{}/".format(config.token)
con = sqlite3.connect('messages.db')
con.create_function('regexp', 2, lambda x, y: 1 if re.search(x,y) else 0)

def get_updates(offset = None):
    url = base + "getUpdates?timeout=50"
    if offset:
        url = url + "&offset={}".format(offset + 1)
    r = requests.get(url)
    return json.loads(r.content)

def send_message(message, chat_id):
    url = base + "sendMessage?chat_id={}&text={}".format(chat_id, message)
    if message is not None:
        r = requests.get(url)
        return json.loads(r.content)
    return None

def get_previous_message_containing(message_info, string):
    chat_id = message_info["chat_id"]
    reply_to_id = message_info["reply_to_message_id"]
    cur = con.cursor()
    query = "SELECT MessageID, SenderName, SenderID, ChatID, Message, ReplyToMessageID FROM messages WHERE Message REGEXP ? AND ChatID = ? "
    parameters = (string, chat_id)
    if reply_to_id != None:
        query += "AND MessageID = ? "
        parameters += (reply_to_id,)
    query += "ORDER BY MessageID DESC"
    cur.execute(query, parameters)
    return cur.fetchone()

def random_insult_reply():
    insult_replies = ["no u", "take that back", "contribute to make me better", "stupid human", "sTuPiD bOt1!1", "lord, have mercy: they don't know that they're saying."]
    return random.choice(insult_replies)

def random_compliment_reply():
    compliment_replies = ["t-thwanks s-senpaii *starts twerking*", "at your service, sir", "thank youu!!", "good human"]
    return random.choice(compliment_replies)

def get_roulette():
    if random.randint(0, 5) == 0:
        return "OH SHIIii.. you're dead, lol."
    return "Eh.. you survived."

def get_reply(message_info):
    reply = None
    message = message_info["message"]
    message_lowercase = message.lower()
    if message is not None:
        if message.startswith(".roulette"):
            return get_roulette()
        if message.startswith("rand"):
            message = message[4:];
            if message.startswith("(") and message.endswith(")"):
                message = message[1:-1]
                message.replace(" ", "")
                split = message.split(",", 1)
                min = split[0]
                max = split[1]
                if(min <= max):
                    return (random.randint(int(min), int(max)))
        if "stupid bot" in message_lowercase or "bad bot" in message_lowercase:
            return random_insult_reply()
        if "good bot" in message_lowercase:
            return random_compliment_reply()
        pat = re.compile('s/.*/.*[/g]*')
        if re.fullmatch(pat, message):
            replace_all = False
            if message.endswith("/"):
                message = message[:-1]
            if message.endswith("/g") and (message.count("/") > 2):
                replace_all = True
                message = message[:-2]
            split = message.split("/", 2)
            if len(split) != 3:
                return None
            old = split[1]
            new = split[2]
            is_valid = False
            try:
                re.compile(old)
            except re.error:
                return None
            reply_info = get_previous_message_containing(message_info, old)
            max_replace = 1
            if replace_all:
                max_replace = len(reply_info[4])
            if reply_info != None:
                reply = re.sub(old, new, reply_info[4], max_replace)
                reply = "<" + reply_info[1] + ">: " + reply
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
                    cur = con.cursor()
                    con.execute("INSERT INTO messages (MessageID, SenderName, SenderID, ChatID, Message, ReplyToMessageID) VALUES (?, ?, ?, ?, ?, ?)", (message_id, sender_name, sender_id, chat_id, message, reply))
                    con.commit()
                    if reply != None:
                        sent_message = send_message(reply, chat_id)
                        sent_message_id = sent_message["result"]["message_id"]
                        sent_message_sender_name = sent_message["result"]["from"]["first_name"]
                        sent_message_sender_id = sent_message["result"]["from"]["id"]
                        con.execute("INSERT INTO messages (MessageID, SenderName, SenderID, ChatID, Message) VALUES (?, ?, ?, ?, ?)", (sent_message_id, sent_message_sender_name, sent_message_sender_id, chat_id, reply))
                        con.commit()
start_bot()
