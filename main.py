# bot.py
import telebot
import spacy
from my_token import token
from data import contacts

bot = telebot.TeleBot(token)

# Загружаем предварительно обученную модель spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_name = message.from_user.username
    question = message.text.lower()

    # Используем spaCy для анализа вопроса
    doc = nlp(question)

    # Извлекаем ключевые фразы с учетом их длины
    keywords = [token.text for token in doc if token.is_alpha and len(token.text) > 2]

    # Обработка ключевых фраз и поиск ответа
    answer = search_answer(keywords, question)

    if answer:
        group = answer.get("group", "")
        reply_message = f"пользователь: {user_name}\nсообщение вопрос: {question}\nвероятный ответ на вопрос: {answer['response']}"
        bot.reply_to(message, reply_message)
    else:
        reply_message = f"пользователь: {user_name}\nсообщение вопрос: {question}\nвероятный ответ на вопрос: Не найдено"
        print("Не найдено ответа на вопрос:", question)

    print(reply_message)


def search_answer(keywords, question):
    best_match = {"group": "", "response": ""}
    max_score = 0

    for group, data in contacts.items():
        for category, info in data.items():
            for keyword, response in info.items():
                # Добавляем проверку наличия ключевых слов, указывающих на запрос телефона, ссылки или адреса
                phone_keywords = ["телефон", "phone"]
                link_keywords = ["ссылка", "сайт", "url", "link"]
                address_keywords = ["адрес", "address"]

                if category.lower() == "контакты" and (any(word in phone_keywords for word in keywords) or any(
                        word in link_keywords for word in keywords) or any(
                        word in address_keywords for word in keywords)):
                    phone_score = sum(word in phone_keywords for word in keywords) + sum(
                        word in response.lower() for word in phone_keywords)
                    link_score = sum(word in link_keywords for word in keywords) + sum(
                        word in response.lower() for word in link_keywords)
                    address_score = sum(word in address_keywords for word in keywords) + sum(
                        word in response.lower() for word in address_keywords)

                    # Если запрос на телефон, пропускаем, если в ответе не телефон; аналогично для ссылок и адреса
                    if any(word in phone_keywords for word in keywords) and not phone_score:
                        continue
                    if any(word in link_keywords for word in keywords) and not link_score:
                        continue
                    if any(word in address_keywords for word in keywords) and not address_score:
                        continue

                    score = sum(word in keyword.lower() for word in keywords) + sum(
                        word in response.lower() for word in keywords)
                    if score > max_score:
                        max_score = score
                        best_match = {"group": group, "response": response}

    # Если вопрос содержит явное указание на группу, выбираем ответ из этой группы
    for group in contacts.keys():
        if group.lower() in question:
            if any(word in phone_keywords for word in keywords):
                return {"group": group, "response": contacts[group]["контакты"]["телефон"]}
            elif any(word in address_keywords for word in keywords):
                return {"group": group, "response": contacts[group]["контакты"]["адрес"]}

    return best_match if max_score > 0 else None


if __name__ == "__main__":
    bot.polling(none_stop=True)
