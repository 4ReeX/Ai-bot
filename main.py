# main.py
import telebot
import spacy
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

def find_answer(question):
    if question.lower() in contacts_data:
        return contacts_data[question.lower()]
    else:
        return None

def is_interesting_question(doc):
    interesting_keywords = {"какой", "есть у кого-нибудь", "дайте", "поделитесь"}
    return any(token.text.lower() in interesting_keywords for token in doc)

bot = telebot.TeleBot(read_token())
nlp = load_spacy_model()

@bot.message_handler(func=lambda message: True)
def reply_to_message(message):
    chat_id = message.chat.id
    sender_name = message.from_user.first_name
    group_name = message.chat.title if message.chat.title else "Private Chat"

    print(f"Received message in group {group_name} from {sender_name}: {message.text}")

    if nlp is not None:
        doc = nlp(message.text)
        print("Tokens:", [token.text for token in doc])
        print("Entities:", [ent.text for ent in doc.ents])

        if is_interesting_question(doc):
            for ent in doc.ents:
                answer = find_answer(ent.text)
                if answer:
                    reply_text = f"Контакты для {ent.text}: Телефон: {answer.get('телефон', 'Нет данных')}, Адрес: {answer.get('адрес', 'Нет данных')}"

                    if 'link' in answer:
                        reply_text += f", Ссылка на чат: {answer['link']}"
                    if 'working_hours' in answer:
                        reply_text += f", Часы работы: {answer['working_hours']}"

                    bot.send_message(chat_id, reply_text, reply_to_message_id=message.message_id)
                    return

    reply_text = "Автоответ, этот ответ потом уберем"
    bot.send_message(chat_id, reply_text, reply_to_message_id=message.message_id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
