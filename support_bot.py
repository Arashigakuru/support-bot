import logging
import telebot
from datetime import datetime
from telebot import types

# Your bot token
TOKEN = 'ENTER_YOUR_TOKEN'

# Bot owner ID (your ID)
OWNER_ID = 'ENTER_OWNER_ID'

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Creating a bot instance
bot = telebot.TeleBot(TOKEN)

# User states
user_states = {}
# List of blocked users
blocked_users = []

# Loading list blocked users from file
def load_blocked_users():
    try:
        with open("blockedusers.txt", "r") as file:
            blocked_users.extend(file.read().splitlines())
    except FileNotFoundError:
        pass

# For add user to block list
def save_blocked_users():
    with open("blockedusers.txt", "w") as file:
        file.write("\n".join(blocked_users))

# The /start command handler
@bot.message_handler(commands=['start'])
def start(message):
    if str(message.chat.id) in blocked_users:
        bot.send_message(chat_id=message.chat.id, text="You are not allowed to access this bot.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Hello! What would you like to do?\nType /send to send a message\nType /cancel if you changed your mind about sending a message")

# The /send command handler
@bot.message_handler(commands=['send'])
def send_message(message):
    if str(message.chat.id) in blocked_users:
        bot.send_message(chat_id=message.chat.id, text="You are not allowed to access this bot.")
    else:
        # Implementing message sending
        bot.send_message(chat_id=message.chat.id, text="Send your message")
    user_states[message.chat.id] = 'waiting_message'

# Handling messages from the users
def process_message(message):
    if message.content_type == 'text':
        message_text = message.text
    else:
        content_type = message.content_type # Note: replace "message.content_type" to "get_media_content_type(message.content_type)" for get file type names in your native language
        message_text = f"{content_type} (media file)"

    # Getting user information
    user_info = f"From: {message.from_user.id} ({message.from_user.username})" if message.from_user.username else f"From: {message.from_user.id}"

    # Getting current date and time (using server time zone)
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Adding time, user information, and the text of the message for sending to the owner
    admin_message = f"{user_info}\nDate and Time: {date_time}\nMessage Text:\n{message_text}"

    # Sending the message to the bot owner
    if message.content_type == 'photo':
        bot.send_photo(chat_id=OWNER_ID, photo=message.photo[-1].file_id, caption=admin_message)
    elif message.content_type == 'video':
        bot.send_video(chat_id=OWNER_ID, video=message.video.file_id, caption=admin_message)
    elif message.content_type == 'document':
        bot.send_document(chat_id=OWNER_ID, document=message.document.file_id, caption=admin_message)
    elif message.content_type == 'audio':
        bot.send_audio(chat_id=OWNER_ID, audio=message.audio.file_id, caption=admin_message)
    else:
        bot.send_message(chat_id=OWNER_ID, text=admin_message)
    
    bot.send_message(chat_id=message.chat.id, text="Your message send to owner")

    # Checking for the existence of a key in the dictionary and deleting it
    if message.chat.id in user_states:
        del user_states[message.chat.id]

# Please only use this if you want to get file type names in your native language
# def get_media_content_type(content_type):
#    if content_type == 'photo':
#        return 'Enter name in your native language'
#    elif content_type == 'video':
#        return 'Enter name in your native language'
#    elif content_type == 'document':
#        return 'Enter name in your native language'
#    elif content_type == 'audio':
#        return 'Enter name in your native language'
#    else:
#        return content_type

# The /cancel command handler
@bot.message_handler(commands=['cancel'])
def cancel(message):
    if str(message.chat.id) in blocked_users:
        bot.send_message(chat_id=message.chat.id, text="You are not allowed to access this bot.")
    elif message.chat.id in user_states and user_states[message.chat.id] == 'waiting_message':
        # Deleting user state
        del user_states[message.chat.id]
        bot.send_message(chat_id=message.chat.id, text="Operation canceled")
    else:
        bot.send_message(chat_id=message.chat.id, text="No active operation to cancel")

# The /reply command handler
@bot.message_handler(commands=['reply'])
def reply(message):
    if str(message.from_user.id) == OWNER_ID:
        # Getting arguments for /reply command
        command_args = message.text.split(' ', 1)
        if len(command_args) == 2:
            user_id, reply_text = command_args[1].split(' ', 1)
            # Sending reply to the user
            bot.send_message(chat_id=user_id, text=reply_text)
            bot.send_message(chat_id=message.chat.id, text="Reply sent")
        else:
            bot.send_message(chat_id=message.chat.id, text="Incorrect /reply command format")
    else:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to execute this command")

# The /block command handler
@bot.message_handler(commands=['block'])
def block_user(message):
    if str(message.from_user.id) == OWNER_ID:
        # Getting arguments for /block command
        command_args = message.text.split(' ', 1)
        if len(command_args) == 2:
            user_id = command_args[1]
            if user_id != OWNER_ID:
                if user_id in blocked_users:
                    bot.send_message(chat_id=message.chat.id, text="This user is already blocked!")
                else:
                    blocked_users.append(user_id)
                    save_blocked_users()
                    bot.send_message(chat_id=message.chat.id, text=f"User with ID {user_id} blocked")
            else:
                bot.send_message(chat_id=message.chat.id, text="You cannot block yourself")
        else:
            bot.send_message(chat_id=message.chat.id, text="Incorrect /block command format")
    else:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to execute this command")

# The /unblock command handler
@bot.message_handler(commands=['unblock'])
def unblock_user(message):
    if str(message.from_user.id) == OWNER_ID:
        # Getting arguments for /unblock command
        command_args = message.text.split(' ', 1)
        if len(command_args) == 2:
            user_id = command_args[1]
            if user_id in blocked_users:
                blocked_users.remove(user_id)
                save_blocked_users()
                bot.send_message(chat_id=message.chat.id, text=f"User with ID {user_id} unblocked")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"User with ID {user_id} is not blocked")
        else:
            bot.send_message(chat_id=message.chat.id, text="Incorrect /unblock command format")
    else:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to execute this command")

# Media files handler
@bot.message_handler(content_types=['photo', 'video', 'document', 'audio'])
def handle_media(message):
    if str(message.chat.id) in blocked_users:
        bot.send_message(chat_id=message.chat.id, text="You are not allowed to access this bot.")
    else:
        if message.chat.id in user_states and user_states[message.chat.id] == 'waiting_message':
            process_message(message)
        else:
            bot.send_message(chat_id=message.chat.id, text="Unknown command")

# Text messages handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) in blocked_users:
        bot.send_message(chat_id=message.chat.id, text="You are not allowed to access this bot.")
    elif message.content_type == 'text':
        if message.chat.id in user_states and user_states[message.chat.id] == 'waiting_message':
            process_message(message)
        else:
            bot.send_message(chat_id=message.chat.id, text="Unknown command")
    else:
        bot.send_message(chat_id=message.chat.id, text="Unknown message type")

# Load the list of blocked users
load_blocked_users()

# Run bot
bot.polling()
