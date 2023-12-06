# main.py
import telebot
import spacy
from debug import reply_to_question_debug
from data import contacts_data


def read_token():
    with open("token.txt", "r") as file:
        token = file.read().strip()
    return token


def load_spacy_model():
    try:
        return spacy.load("ru_core_news_lg")
    except Exception as e:
        print(f"Error loading spaCy model: {e}")
        return None


if __name__ == "__main__":
    bot = telebot.TeleBot(read_token())
    nlp = load_spacy_model()


    @bot.message_handler(func=lambda message: True)  # Изменил условие
    def reply_to_question(message):
        # Передаем contacts_data в функцию
        reply_to_question_debug(message, nlp, contacts_data)


    bot.polling(none_stop=True)
