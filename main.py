# main.py
import telebot
import spacy
from debug import reply_to_question_debug
from data import contacts_data

bot = telebot.TeleBot("6817644370:AAENrfIyNemlJ1-7GPTlUtWxdn0WBAAmhjM")
nlp = spacy.load("ru_core_news_lg")

@bot.message_handler(func=lambda message: True)
def reply_to_question(message):
    reply_to_question_debug(message, nlp, contacts_data)

bot.polling(none_stop=True)
