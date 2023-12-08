# debug.py
import telebot
import spacy
from fuzzywuzzy import process

nlp = spacy.load("ru_core_news_lg")

TOKEN = '6817644370:AAENrfIyNemlJ1-7GPTlUtWxdn0WBAAmhjM'
bot = telebot.TeleBot(TOKEN)


def find_most_relevant_entity(normalized_text, contacts_data):
    doc = nlp(normalized_text)

    # Собираем все ключевые слова из вопроса
    keywords = set([token.text.lower() for token in doc if token.text.lower() not in contacts_data])

    # Определяем релевантное слово из вопроса
    relevant_word = None
    for token in doc:
        if token.text.lower() in keywords:
            relevant_word = token.text.lower()
            break

    return relevant_word


def normalize_text(text):
    return text.lower()


def log_message_info(message, normalized_text, detected_entities):
    sender_name = message.from_user.first_name
    group_name = message.chat.title if message.chat.title else "Private Chat"

    print(f"debug: сообщение из группы {group_name} от пользователя {sender_name}: {message.text}")
    print(f"Токены: {normalized_text.split()}")
    print(f"Вхождения: {detected_entities}")
    print("\n")


def reply_to_question_debug(message, nlp, contacts_data):
    normalized_text = normalize_text(message.text)
    detected_entities = []

    log_message_info(message, normalized_text, detected_entities)

    if nlp is not None:
        doc = nlp(normalized_text)

        print("Токены spaCy:", [token.text for token in doc])
        print("Леммы spaCy:", [token.lemma_ for token in doc])
        print("POS spaCy:", [(token.text, token.pos_) for token in doc])
        print("NER spaCy:", [(ent.text, ent.label_) for ent in doc.ents])

        for ent in doc.ents:
            detected_entities.append((ent.text, ent.label_))

    target_entity = get_dynamic_target_entity(normalized_text, contacts_data, detected_entities)
    answer = find_answer(normalized_text, contacts_data, target_entity=target_entity)

    reply_text = f"Ответ на ваш вопрос '{normalized_text}': {answer}"
    bot.send_message(message.chat.id, reply_text)

    detected_topics = [entity[0] for entity in detected_entities]
    print(f"Обнаруженные темы: {detected_topics}")

    return reply_text


def get_dynamic_target_entity(normalized_text, contacts_data, detected_entities):
    for ent_text, ent_label in detected_entities:
        if ent_label == "ORG" or ent_label == "PHONE" or ent_label == "EMAIL":
            return ent_text.lower()

    for key in contacts_data:
        ratio = process.extractOne(normalized_text, [key], score_cutoff=70)
        if ratio:
            return key.lower()

    return None


def find_answer(normalized_text, contacts_data, target_entity=None):
    keywords = normalized_text.split()

    if target_entity:
        keywords.append(target_entity)

    current_data = contacts_data

    for keyword in keywords:
        if keyword in current_data:
            current_data = current_data[keyword]
        else:
            return None

    return current_data
