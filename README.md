# sadbot
a simple telegram bot.  
Which main feature is its sed command, the famous UNIX command.

## Dependencies
The bot has the following dependencies:
- `requests`

Which can be installed with:
```
pip3 install -r requirements.txt \
             -r dev-requirements.txt # Add this when developing the bot
```

## Installation
Place your bot token in the config file:
```
sed -i 's/placeholder/YOURTOKENHERE' config.py
```

## Usage
Here's how you run the bot manually:  
```
nohup python3 sadbot & disown
```
Alternatively, you can create a new systemd service, which handles the bot restart
restart in a more neat way, with these commands:
```
sed -i 's/userplaceholder/BOTUSER' sadbot.service
sed -i 's/pathplaceholder/BOTPATH' sadbot.service
sudo cp sadbot.service /etc/systemd/system/
sudo service sadbot start
```
And to check the bot status you can simply type:
```
service sadbot status
```

## Todo
- [ ] Place the bot commands in modules which can be unplugged from the
main application (?).
- [ ] Put everything in a class.
- [ ] Pass the database connection through dependency injection, to the
functions that require it.
