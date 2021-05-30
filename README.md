# sadbot
A simple telegram bot.  
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
You have to place your bot token either in the environment variables or in the
config files, by manually editing them:
```
nano sadbot/config.py
nano Dockerfile # If you are using Docker/Podman
```
In the `sadbot/config.py` file you can also find the settings for configurable
bot commands (like `cringe`, `roulette` etc.)


## Usage
### Manual
Here's how you run the bot manually:  
```
nohup PYTHONPATH=. python3 -m sadbot & disown
```
### Systemd Service
Alternatively, you can create a new systemd service, which handles the bot
restart in a way more neat way, with these commands:
```
sed -i 's/userplaceholder/BOTUSER' sadbot.service
sed -i 's/pathplaceholder/BOTPATH' sadbot.service
sudo cp sadbot.service /etc/systemd/system/
sudo systemctl daemon-reload
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
### Docker/Podman
If you like docker or podman, you can easily build the container using the
Dockerfile:
```
sudo docker build -m sadbot .
```
Then you can easily start the bot with:
```
sudo docker run -it sadbot
```

## Todo list
- [ ] Add media support for outgoing messages
- [X] Fix the roulette code
- [ ] Eval command
- [ ] Weather command
- [ ] Status command
- [ ] Seen command
- [ ] Tay command
- [ ] User ratelimit
- [ ] Group ratelimit
- [ ] Antiflood, samewords count and newlines count
- [ ] FBI watchlist
- [ ] Captcha command
- [X] Translate command
