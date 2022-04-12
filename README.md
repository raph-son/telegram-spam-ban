# telegram-spam-ban
Ban users that meet certain spam criteria 

## Usage
To begin, you'll need to get telegram `ID` and `hash`
[Check here](https://docs.telethon.dev/en/stable/basic/signing-in.html) on how to set that up

Once done open `ban.py` and add your `ID` and `hash` and your `channel ID` 

run `pip install -r requirements.py` to install needed requirements and also, run `python db.py` to set you local db up

You can spin the bot on with `python ban.py` or to add tags that will be checked on users account do `python ban.py support,admin` for example to check users with the name 'admin' or 'support' 
