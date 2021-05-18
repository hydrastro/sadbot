"""a sad telegram bot"""

import json
import random
import re
import sqlite3
import requests
import config
import os


class Message:
    """message class"""

    def __init__(
        self,
        message_id: int = 0,
        sender_name: str = "",
        sender_id: int = 0,
        chat_id: int = 0,
        text: str = "",
        reply_to_message_id: int = 0,
    ) -> None:
        self.messageID = message_id
        self.senderName = sender_name
        self.senderID = sender_id
        self.messageText = text
        self.chatID = chat_id
        self.replyID = reply_to_message_id


class App:
    """main app class. when called it starts the bot"""

    def __init__(self) -> None:
        self.DB = sqlite3.connect("messages.db")
        self.DB.create_function("regexp", 2, lambda x, y: 1 if re.search(x, y) else 0)
        token = config.token
        if os.getenv("TOKEN"):
            token = os.getenv("TOKEN")
        self.baseURL = "https://api.telegram.org/bot{}/".format(token)
        self.DB.execute(
            "CREATE TABLE IF NOT EXISTS messages (    MessageID        integer,\
    SenderName       text,\
    SenderID         int,\
    ChatID           integer,\
    Message          text,\
    ReplyToMessageID int\
)"
        )
        self.startBot()

    def getUpdates(self, offset=None):
        """retrieves updates from the telelegram API"""

        url = self.baseURL + "getUpdates?timeout=50"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        req = requests.get(url)
        return json.loads(req.content)

    def sendMessage(self, message: Message):
        """sends message to some chat using api"""

        url = self.baseURL + "sendMessage?chat_id={}&text={}".format(
            message.chatID, message.messageText
        )
        if message is not None:
            req = requests.get(url)
            return json.loads(req.content)
        return None

    def getPreviousMessage(self, message: Message, reg: str) -> Message:
        """retrieves a previous message from the database matching a certain regex pattern"""

        cur = self.DB.cursor()
        query = (
            "SELECT MessageID, SenderName, SenderID, ChatID, Message, "
            "ReplyToMessageID FROM messages WHERE Message REGEXP ? AND ChatID = ? "
        )
        params = (reg, message.chatID)
        if message.replyID is not None:
            query += "AND MessageID = ? "
            params += (message.replyID,)
        query += "ORDER BY MessageID DESC"
        cur.execute(query, params)
        data = cur.fetchone()
        mes = Message(
            message_id=data[0],
            sender_name=data[1],
            sender_id=data[2],
            chat_id=data[3],
            text=data[4],
            reply_to_message_id=data[5],
        )
        return mes

    def randomInsult(self) -> str:
        """gets a reply for when the bot receives an insult"""

        insult_replies = [
            "no u",
            "take that back",
            "contribute to make me better",
            "stupid human",
            "sTuPiD bOt1!1",
            "lord, have mercy: they don't know that they're saying.",
        ]
        return random.choice(insult_replies)

    def randomCompliment(self) -> str:
        """gets a reply for when the bot receives a compliment"""

        compliment_replies = [
            "t-thwanks s-senpaii *starts twerking*",
            "at your service, sir",
            "thank youu!!",
            "good human",
        ]
        return random.choice(compliment_replies)

    def getRoulette(self) -> str:
        """plays the russian roulette"""

        if random.randint(0, 5) == 0:
            return "OH SHIIii.. you're dead, lol."
        return "Eh.. you survived."

    def getClosedThread(self) -> str:
        """closes a discussion"""

        closed_thread_replies = [
            "rekt",
            "*This thread has been archived at RebeccaBlackTech*",
        ]
        return random.choice(closed_thread_replies)

    def getRandCommand(self, message: Message) -> str:
        """returns a random number in a user-defined range"""

        text = message.messageText[4:]
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
            text.replace(" ", "")
            split = text.split(",", 1)
            min_rand = split[0]
            max_rand = split[1]
            if min_rand <= max_rand:
                return str(random.randint(int(min_rand), int(max_rand)))
        return None

    def getSedCommand(self, message: Message) -> str:
        """performs the sed command to a message"""

        replace_all = False
        text = message.messageText
        if text.endswith("/"):
            text = text[:-1]
        if text.endswith("/g") and (text.count("/") > 2):
            replace_all = True
            text = text[:-2]
        first_split = text.split("/", 1)
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
        reply_message = self.getPreviousMessage(message, old)
        if reply_message is None:
            return None
        max_replace = 1
        if replace_all:
            max_replace = len(reply_message.messageText)
        if reply_message is not None:
            try:
                reply = re.sub(old, new, reply_message.messageText, max_replace)
                reply = "<" + reply_message.senderName + ">: " + reply
                return reply
            except re.error:
                return None
        return None

    def getReply(self, message: Message):
        """checks if a bot command is triggered and gets its reply"""
        text = message.messageText
        text_lowercase = text.lower()
        if text is None:
            return None
        if re.fullmatch(re.compile("s/.*/.*[/g]*"), text):
            return self.getSedCommand(message)
        if text_lowercase.startswith(".roulette"):
            return self.getRoulette()
        if text_lowercase == ".roll":
            return random.randint(0, 10)
        if text_lowercase.startswith("rand"):
            return self.getRandCommand(message)
        if "!leaf" in text or "!canadian" in text:
            return "🇨🇦"
        if text_lowercase in ("/thread", "fpbp", "spbp"):
            return self.getClosedThread()
        if text_lowercase in ("stupid bot", "bad bot"):
            return self.randomInsult()
        if text_lowercase == "good bot":
            return self.randomCompliment()
        return None

    def insertMessage(self, message: Message) -> None:
        """inserts a message into the database"""
        query = (
            "INSERT INTO messages (MessageID, SenderName, SenderID, ChatID, Message, "
            "ReplyToMessageID) VALUES (?, ?, ?, ?, ?, ?)"
        )
        self.DB.execute(
            query,
            (
                message.messageID,
                message.senderName,
                message.senderID,
                message.chatID,
                message.messageText,
                message.replyID,
            ),
        )
        self.DB.commit()

    def startBot(self) -> None:
        """starts the bot"""
        update_id = None
        while True:
            updates = self.getUpdates(offset=update_id)
            if "result" in updates:
                updates = updates["result"]
            else:
                continue
            if not updates:
                continue
            for item in updates:
                update_id = item["update_id"]
                try:
                    text = str(item["message"]["text"])
                except:
                    continue
                if text is None:
                    continue
                message_id = item["message"]["message_id"]
                sender_name = item["message"]["from"]["first_name"]
                sender_id = item["message"]["from"]["id"]
                chat_id = item["message"]["chat"]["id"]
                reply_to_message_id = None
                if "reply_to_message" in item["message"]:
                    reply_to_message_id = item["message"]["reply_to_message"][
                        "message_id"
                    ]
                message = Message(
                    message_id,
                    sender_name,
                    sender_id,
                    chat_id,
                    text,
                    reply_to_message_id,
                )
                reply = self.getReply(message)
                self.insertMessage(message)
                if reply is None:
                    continue
                new_message = Message(chat_id=message.chatID, text=reply)
                sent_message = self.sendMessage(new_message)
                if sent_message is not None and "result" in sent_message:
                    sent_message_id = sent_message["result"]["message_id"]
                    sent_message_sender_name = sent_message["result"]["from"][
                        "first_name"
                    ]
                    sent_message_sender_id = sent_message["result"]["from"]["id"]
                    message = Message(
                        sent_message_id,
                        sent_message_sender_name,
                        sent_message_sender_id,
                        message.chatID,
                        reply,
                        None,
                    )
                    self.insertMessage(message)


if __name__ == "__main__":
    app = App()
