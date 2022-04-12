"""
Ban users with names as admin or names match certain conditions
"""
import sys
from datetime import timedelta

from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins

import db

API_ID = 
API_HASH = ""
CHANNEL_ID = 

client = TelegramClient("client",  API_ID, API_HASH)

async def main():
    cmd = None
    try:
        cmd = [i for i in sys.argv[1].split(',')]
    except IndexError:
        pass
    if cmd:
        # add to sqlite
        db.insert(cmd)

    tags = db.select()
    tags = [tag[0] for tag in tags]
    
    admin_names = []
    chat = await client.get_entity(CHANNEL_ID)
    async for user in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
        first_name = None
        last_name = None
        if user.first_name:
            first_name = user.first_name.lower()
        if user.last_name:
            last_name = user.last_name.lower()
        admin_names.append([user.id, first_name, last_name])

    async for user in client.iter_participants(chat, aggressive=False):
        status = True
        for admin in admin_names:
            if user.id != admin[0]: # Only look into non-admins
                if user.first_name or user.last_name:
                    if ((user.first_name == admin[1]) and (user.last_name == admin[2]) or (user.first_name == admin[2]) and (user.last_name == admin[1])):
                        # ban user
                        await client.edit_permissions(chat, user, timedelta(minutes=0),
                              view_messages=False)
                        status = False
                        break
        if status: # User pass admin check
            if user.first_name or user.last_name:
                if user.username.lower() in tags or user.first_name in tags or user.last_name in tags:
                    await client.edit_permissions(chat, user, timedelta(minutes=0), view_messages=False)
                    break
    db.close()


with client:
    client.loop.run_until_complete(main())

