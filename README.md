# sadbot
a simple telegram bot.

## Usage
Create the database via
```
cat createdb.sql | sqlite3 messages.db
```
Then, you need to place your bot token:  
`sed -i 's/placeholder/YOURTOKENHERE' bot.py`  

Then, here's how you run the bot:  
`nohup python3 bot.py & disown`
