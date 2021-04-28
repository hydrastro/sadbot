# sadbot
a simple telegram bot.

## Installation
Create the database via:
```
cat createdb.sql | sqlite3 messages.db
```
Then, place your bot token in the config file:  
```
sed -i 's/placeholder/YOURTOKENHERE' config.py
```

## Usage
Here's how you run the bot:  
```
nohup python3 bot.py & disown
```
