#Helper Documentation
#https://python-telegram-bot.readthedocs.io/en/stable/

import logging
import time

from flask import Flask, request # A request will contain all information about certain Url
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from telegram import Bot, Update, ReplyKeyboardMarkup
from utils import get_reply, fetch_news, topics_keyboard

#Enable logging

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "1156199726:AAHvP1aCaR17urWdK5WZLhwiUprpCTf4UNk"

#Flask app object 
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello!"

@app.route(f'/{TOKEN}', methods = ['GET', 'POST'])
def webhook():
#Webhook view which recieves updates from telegram
#Create update object from json-format request data
    update = Update.de_json(request.get_json(), bot)
    #process update
    dp.process_update(update)
    return "Okay!"

#any function which are passed
# in CommandHandler It will take two argument:-
# bot, update
def start(bot,update):
    print(update)
#update object have message object in which
# you have from_user value and in that first_name
    author = update.message.from_user.first_name
    #msg = update.message.text #It is will contain actual text from the user ou author
    reply = "Hi! {}".format(author)
    bot.send_message(chat_id = update.message.chat_id, text = reply)

def _help(bot, update):
    help_txt = "Hey! This is a help text."
    bot.send_message(chat_id = update.message.chat_id, text = help_txt)

def news(bot, update):
    """callback function for /news handler"""
    bot.send_message(chat_id=update.message.chat_id, text="Choose a category",
                     reply_markup=ReplyKeyboardMarkup(keyboard=topics_keyboard, one_time_keyboard=True)) #Reply keyboard will create a keyboard whereas user has to type something whereas in inlinekeyboard is create just below the text


def reply_text(bot, update):
    intent, reply = get_reply(update.message.text, update.message.chat_id)
    if intent == "get_news":
        articles = fetch_news(reply)
        for article in articles:
            bot.send_message(chat_id=update.message.chat_id, text=article['link'])
    else:
        bot.send_message(chat_id=update.message.chat_id, text=reply)

def echo_sticker(bot, update):
    bot.send_sticker(chat_id = update.message.chat_id, sticker = update.message.sticker.file_id)


def error(bot,update):
    logger.error("Update '%s' caused error '%s'", update, update.error)



#Kept outside of __main__ because now python file run through gunicorn not by our localhost server
bot = Bot(TOKEN)
#ngrok generates public URL for local host application
#ngrok is a free tool that allows us to tunnel from a public URL to our application running locally
#Telegram currently support for webhooks: 443, 80, 88, 8443. These four are port Number which must be same as Flask 
#bot.set_webhook("https://c0164b3dcf9d.ngrok.io/" + TOKEN)

try:
    bot.set_webhook("https://radiant-garden-20965.herokuapp.com/" + TOKEN)
    time.sleep(5)
except Exception as e:
    print(e)

#update_queue is passed as None because there is no threading
dp = Dispatcher(bot, None)

#Handling the commands
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", _help))
dp.add_handler(CommandHandler("news", news))
dp.add_handler(MessageHandler(Filters.text, reply_text))
dp.add_handler(MessageHandler(Filters.sticker, echo_sticker))
dp.add_error_handler(error)


if __name__ == "__main__":
    app.run(port = 8443) #Through this we can run our Flask appliation(this code) on localhost server