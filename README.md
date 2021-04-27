# sadbot
a simple telegram bot.

## Installation
Create the database via:
```
cat createdb.sql | sqlite3 messages.db
```
Then, place your bot token:  
```
sed -i 's/placeholder/YOURTOKENHERE' bot.py
```  
## Usage
Here's how you run the bot:  
```
nohup python3 bot.py & disown
```
