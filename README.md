# sadbot
a simple telegram bot.

## Dependencies
The bot has the following dependencies:
- `requests`
Which can be installed with:
```
pip3 install requests
```

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
Here's how you run the bot manually:  
```
nohup python3 bot.py & disown
```
Alternatively, you can create a new systemd service,
which handles the bot restart, with these commands:   
```
sed -i 's/userplaceholder/BOTUSER' sadbot.service
sed -i 's/pathplaceholder/BOTPATH' sadbot.service
sudo cp sadbot.service /etc/systemd/system/
sudo systemctl start sadbot
```
