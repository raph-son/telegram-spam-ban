"""
Ban users with names as admin or names match certain conditions on entering
"""
import logging

from typing import Tuple, Optional

from telegram import Update, Bot, Chat, ChatMember, ParseMode, ChatMemberUpdated
from telegram.ext import Updater, CommandHandler, CallbackContext, ChatMemberHandler

from db import DB

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

db = DB()

CHAT_ID =
BOT_TOKEN = ''

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

bot = Bot(token=BOT_TOKEN)
ADMINS = bot.get_chat_administrators(CHAT_ID)

def get_admins():
    names = set()
    for admin in ADMINS:
        if admin.user.first_name:
            names.add(admin.user.first_name.lower())
        if admin.user.last_name:
            names.add(admin.user.last_name.lower())
    return names

def extract_status_change(chat_member_update: ChatMemberUpdated):
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = (
        old_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
        new_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member

def new_chat_members(update: Update, context: CallbackContext) -> None:
    # New user in chat
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        ban_tags = db.select("tags", "tag")
        user = update.chat_member.new_chat_member.user
        first_name = ""
        last_name = ""
        if user.first_name:
            first_name = user.first_name.lower()
        if user.last_name:
            last_name = user.last_name.lower()
        if first_name or last_name:
            admin_names = get_admins()
            id = user.id
            username = user.username
            if (first_name in admin_names) or (last_name in admin_names):
                # ban user
                bot.ban_chat_member(CHAT_ID, user.id, until_date=0)
                db.insert_users(id, username)
            else:
                for tag in ban_tags:
                    tag = tag[0]
                    if first_name == tag.lower() or last_name == tag.lower() or user.username.lower() == tag.lower():
                        bot.ban_chat_member(CHAT_ID, user.id, until_date=0)
                        db.insert_users(id, username)

def add(update: Update, context: CallbackContext):
    if update.message.from_user.id in [admin.user.id for admin in ADMINS]: # Make sure only admin can use Bot
        tags = update.message.text.split(" [") # example /admin ['admin', 'support']
        if len(tags) == 2:
            tags = tags[1].strip('][').strip("'").strip('"').split(', ')
            for tag in tags:
                db.insert(tag.replace("'",""), "tags", "tag")

def view(update: Update, context: CallbackContext):
    if update.message.from_user.id in [admin.user.id for admin in ADMINS]: # Make sure only admin can use Bot
        users_ = db.select("users", "username")
        if users_:
            users = [user for user in users_[0]]
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"{users}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No User Banned yet")

def remove(update: Update, context: CallbackContext):
    if update.message.from_user.id in [admin.user.id for admin in ADMINS]: # Make sure only admin can use Bot
        tags = update.message.text.split(" [") # example /admin ['admin', 'support']
        if len(tags) == 2:
            users = tags[1].strip('][').strip("'").strip('"').split(', ')
            for user in users:
                id = db.select_users(user)
                for id_ in id:
                    bot.unban_chat_member(CHAT_ID, id_, True)
                    db.remove(id_)

add_handler = CommandHandler('add', add)
view_handler = CommandHandler('view', view)
remove_handler = CommandHandler('remove', remove)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(view_handler)
dispatcher.add_handler(remove_handler)

dispatcher.add_handler(ChatMemberHandler(new_chat_members, ChatMemberHandler.CHAT_MEMBER))

updater.start_polling(allowed_updates=Update.ALL_TYPES)

updater.idle()
