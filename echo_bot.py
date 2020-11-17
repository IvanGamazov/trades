import telebot
from telebot import apihelper


apihelper.proxy = {'https': 'socks5://alexstav_bot:hxhqhyiq@167.71.53.214:1080'}
bot = telebot.TeleBot("1125563549:AAFVJyN1Em2itQr26fGLCAxXGcizvrxcHlk")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

#@bot.message_handler(func=lambda message: True)
#def echo_all(message):
#	bot.reply_to(message, message.text)

@bot.message_handler(commands=['new'])
def new_cars(message):
	bot.reply_to(message, "Новые объявления:")

@bot.message_handler(commands=['all'])
def all_cars(message):
	bot.send_message(message.chat.id, "Все объявления:")

bot.polling()