# debug.py
import telebot
import spacy
from fuzzywuzzy import process

nlp = spacy.load("ru_core_news_lg")

TOKEN = '6817644370:AAENrfIyNemlJ1-7GPTlUtWxdn0WBAAmhjM'
bot = telebot.TeleBot(TOKEN)


def find_most_relevant_entity(normalized_text, contacts_data):
    doc = nlp(normalized_text)

    # Собираем все сущности из вопроса
    entities = set([ent.text.lower() for ent in doc.ents])

    # Определяем релевантное слово из вопроса
    relevant_word = None
    for token in doc:
        if token.text.lower() not in entities:
            relevant_word = token.text.lower()
            break

    return relevant_word


def normalize_text(text):
    # Здесь можете реализовать функцию нормализации текста по вашему усмотрению
    return text.lower()  # В этом примере мы просто приводим текст к нижнему регистру


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

    log_message_info(message, normalized_text, detected_entities)  # Выводим отладочную информацию

    if nlp is not None:
        doc = nlp(normalized_text)

        # Выводим дополнительные данные из spaCy
        print("Токены spaCy:", [token.text for token in doc])
        print("Леммы spaCy:", [token.lemma_ for token in doc])
        print("POS spaCy:", [(token.text, token.pos_) for token in doc])
        print("NER spaCy:", [(ent.text, ent.label_) for ent in doc.ents])

        for ent in doc.ents:
            detected_entities.append((ent.text, ent.label_))

    # Поиск ответа в данных
    # Добавляем логику для динамической установки target_entity
    target_entity = get_dynamic_target_entity(normalized_text, contacts_data)
    answer = find_answer(normalized_text, contacts_data)

    # Отправка ответа обратно в чат
    reply_text = f"Ответ на ваш вопрос '{normalized_text}': {answer}"
    bot.send_message(message.chat.id, reply_text)

    return reply_text


def get_dynamic_target_entity(normalized_text, contacts_data):
    # Добавьте вашу логику по определению динамического target_entity
    # Например, можно использовать process.extractOne для сопоставления текста и выбрать наилучшее совпадение
    # Верните ключ (название сущности), которое соответствует наилучшему совпадению

    # В примере возвращаем первый найденный ключ
    for key in contacts_data:
        ratio = process.extractOne(normalized_text, [key], score_cutoff=70)
        if ratio:
            return key

    # Если ничего не найдено, возвращаем None
    return None


def find_answer(normalized_text, contacts_data):
    # Определяем наиболее релевантное слово из вопроса
    target_entity = find_most_relevant_entity(normalized_text, contacts_data)

    # Проходим по всем ключам в словаре
    for key in contacts_data:
        # Сравниваем вопрос с каждым ключом с использованием частичного сопоставления
        ratio = process.extractOne(normalized_text, [key], score_cutoff=70)  # Можно настроить порог сопоставления
        if ratio:
            # Проверяем, запрашивается ли конкретная сущность
            if target_entity is not None and target_entity in contacts_data[key]:
                return contacts_data[key][target_entity]
            return contacts_data[key]

    # Если ничего не найдено, возвращаем None
    return None