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
nohup PYTHONPATH=. python3 -m sadbot & disown
```
Alternatively, you can create a new systemd service, which handles the bot restart
restart in a way more neat way, with these commands:
```
sed -i 's/userplaceholder/BOTUSER' sadbot.service
sed -i 's/pathplaceholder/BOTPATH' sadbot.service
sudo cp sadbot.service /etc/systemd/system/
sudo service sadbot start
```
And to check the bot status you can simply type:
```
sudo service sadbot status
```
or, for reading the full log:
```
sudo journalctl -u sadbot.service
```
If you like docker or podman, you can easily build the container using the Dockerfile
```
sudo docker build -m sadbot .
```
Don't forget to either set the token inside of the Dockerfile modifying the 
commented line or change the token inside of `sadbot/config.py` file.
Then you can easily start the bot with
```
sudo docker run -it sadbot
```

## Todo list
- [ ] Place the bot commands in modules which can be unplugged from the
main application (?).
- [ ] Pass the database connection through dependency injection, to the
functions that require it.
