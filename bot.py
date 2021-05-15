"""a sad telegram bot"""

import json
import random
import re
import sqlite3
import requests
import config

BASE = "https://api.telegram.org/bot{}/".format(config.token)
con = sqlite3.connect('messages.db')
con.create_function('regexp', 2, lambda x, y: 1 if re.search(x, y) else 0)

def get_updates(offset=None):
    """retrieves updates from the telelegram API"""
    url = BASE + "getUpdates?timeout=50"
    if offset:
        url = url + "&offset={}".format(offset + 1)
    req = requests.get(url)
    return json.loads(req.content)

def send_message(message, chat_id):
    """sends a message in a certain chat id, using the telegram API"""
    url = BASE + "sendMessage?chat_id={}&text={}".format(chat_id, message)
    if message is not None:
        req = requests.get(url)
        return json.loads(req.content)
    return None

def get_previous_message_containing(message_info, string):
    """retrieves a previous message from the database matching a certain regex pattern"""
    chat_id = message_info["chat_id"]
    reply_to_id = message_info["reply_to_message_id"]
    cur = con.cursor()
    query = "SELECT MessageID, SenderName, SenderID, ChatID, Message, " \
    "ReplyToMessageID FROM messages WHERE Message REGEXP ? AND ChatID = ? "
    parameters = (string, chat_id)
    if reply_to_id is not None:
        query += "AND MessageID = ? "
        parameters += (reply_to_id,)
    query += "ORDER BY MessageID DESC"
    cur.execute(query, parameters)
    return cur.fetchone()

def random_insult_reply():
    """gets a reply for when the bot receives an insult"""
    insult_replies = ["no u", "take that back", "contribute to make me better", \
    "stupid human", "sTuPiD bOt1!1", "lord, have mercy: they don't know that they're saying."]
    return random.choice(insult_replies)

def random_compliment_reply():
    """gets a reply for when the bot receives a compliment"""
    compliment_replies = ["t-thwanks s-senpaii *starts twerking*", "at your service, sir", \
    "thank youu!!", "good human"]
    return random.choice(compliment_replies)

def get_roulette():
    """plays the russian roulette"""
    if random.randint(0, 5) == 0:
        return "OH SHIIii.. you're dead, lol."
    return "Eh.. you survived."

def get_closed_thread_reply():
    """closes a discussion"""
    closed_thread_replies = ["rekt", "*This thread has been archived at RebeccaBlackTech*"]
    return random.choice(closed_thread_replies)

def get_rand_command_reply(message):
    """returns a random number in a user-defined range"""
    message = message[4:]
    if message.startswith("(") and message.endswith(")"):
        message = message[1:-1]
        message.replace(" ", "")
        split = message.split(",", 1)
        min_rand = split[0]
        max_rand = split[1]
        if min_rand <= max_rand:
            return random.randint(int(min_rand), int(max_rand))
    return None

def get_sed_command_reply(message_info):
    """performs the sed command to a message"""
    replace_all = False
    message = message_info["message"]
    if message.endswith("/"):
        message = message[:-1]
    if message.endswith("/g") and (message.count("/") > 2):
        replace_all = True
        message = message[:-2]
    first_split = message.split("/", 1)
    second_split = ["s"]
    second_split += first_split[1].rsplit("/", 1)
    if len(second_split) != 3:
        return None
    old = second_split[1]
    new = second_split[2]
    try:
        re.compile(old)
    except re.error:
        return None
    reply_info = get_previous_message_containing(message_info, old)
    if reply_info is None:
        return None
    max_replace = 1
    if replace_all:
        max_replace = len(reply_info[4])
    if reply_info is not None:
        try:
            reply = re.sub(old, new, reply_info[4], max_replace)
            reply = "<" + reply_info[1] + ">: " + reply
            return reply
        except re.error:
            return None
    return None

def get_reply(message_info):
    """checks if a bot command is triggered and gets its reply"""
    message = message_info["message"]
    message_lowercase = message.lower()
    if message is None:
        return None
    if re.fullmatch(re.compile('s/.*/.*[/g]*'), message):
        return get_sed_command_reply(message_info)
    if message.startswith(".roulette"):
        return get_roulette()
    if message == ".roll":
        return random.randint(0, 10)
    if message.startswith("rand"):
        return get_rand_command_reply(message)
    if "!leaf" in message_lowercase or "!canadian" in message_lowercase:
        return "🇨🇦"
    if message_lowercase in ("/thread", "fpbp", "spbp"):
        return get_closed_thread_reply()
    if message_lowercase in ("stupid bot", "bad bot"):
        return random_insult_reply()
    if message_lowercase == "good bot":
        return random_compliment_reply()
    return None

def insert_message_into_db(message_info):
    """inserts a message into the database"""
    query = "INSERT INTO messages (MessageID, SenderName, SenderID, ChatID, Message, " \
    "ReplyToMessageID) VALUES (?, ?, ?, ?, ?, ?)"
    con.execute(query, list(message_info.values()))
    con.commit()

def start_bot():
    """starts the bot and keeps it running"""
    update_id = None
    while True:
        updates = get_updates(offset=update_id)
        if "result" in updates:
            updates = updates["result"]
        else:
            continue
        if not updates:
            continue
        for item in updates:
            update_id = item["update_id"]
            try:
                message = str(item["message"]["text"])
            except (ValueError, TypeError, KeyError):
                continue
            if message is None:
                continue
            message_id = item["message"]["message_id"]
            sender_name = item["message"]["from"]["first_name"]
            sender_id = item["message"]["from"]["id"]
            chat_id = item["message"]["chat"]["id"]
            reply_to_message_id = None
            if "reply_to_message" in item["message"]:
                reply_to_message_id = item["message"]["reply_to_message"]["message_id"]
            message_info = {"message_id": message_id, "sender_name": sender_name, \
            "sender_id": sender_id, "chat_id": chat_id, "message": message,        \
            "reply_to_message_id": reply_to_message_id}
            reply = get_reply(message_info)
            insert_message_into_db(message_info)
            if reply is None:
                continue
            sent_message = send_message(reply, chat_id)
            if sent_message is not None and "result" in sent_message:
                sent_message_id = sent_message["result"]["message_id"]
                sent_message_sender_name = sent_message["result"]["from"]["first_name"]
                sent_message_sender_id = sent_message["result"]["from"]["id"]
                message_info = {"message_id": sent_message_id, "sender_name": \
                sent_message_sender_name, "sender_id": sent_message_sender_id, \
                "chat_id": chat_id, "message": reply, "reply_to_message_id": None}
                insert_message_into_db(message_info)
start_bot()
