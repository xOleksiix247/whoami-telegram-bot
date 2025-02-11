import telebot
import random
import threading
import time

TOKEN = "ТВОЙ_ТОКЕН_ТУТ"  # Встав свій токен
bot = telebot.TeleBot(TOKEN)

# Великий список персонажів
characters = [
    "Тарас Шевченко", "Елвіс Преслі", "Гаррі Поттер", "Ілон Маск",
    "Леонардо да Вінчі", "Кіт", "Лев", "Телефон", "Рюкзак", "Чебурашка",
    "Шрек", "Термінатор", "Леонель Мессі", "Бетмен", "Гомер Сімпсон",
    "Пірат", "Санта Клаус", "Спанч Боб", "Динозавр", "Гаррі Стайлс"
]

players = {}  # {user_id: персонаж}
scores = {}   # {user_id: очки}

def end_game(user_id, chat_id):
    """Автоматично завершує гру через 60 секунд."""
    time.sleep(60)
    if user_id in players:
        bot.send_message(chat_id, f"⏳ Час вийшов! Ти не вгадав 😢 Це був {players[user_id]}.")
        del players[user_id]

@bot.message_handler(commands=['start'])
def start_game(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.first_name

    # Якщо гравець уже грає
    if user_id in players:
        bot.send_message(chat_id, f"{username}, ти вже граєш! Запитуй, хто ти! 😉")
        return

    # Випадковий персонаж
    character = random.choice(characters)
    players[user_id] = character

    # Додаємо гравця в таблицю рекордів, якщо його ще немає
    if user_id not in scores:
        scores[user_id] = 0

    # Відправляємо персонажа в особисті повідомлення
    bot.send_message(user_id, f"🤫 Твій персонаж: {character}\nЗапитуй: 'Я людина?', 'Я тварина?' тощо.")

    # Запускаємо таймер на 60 секунд
    threading.Thread(target=end_game, args=(user_id, chat_id)).start()

@bot.message_handler(func=lambda message: message.text.lower().startswith("я"))
def ask_question(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in players:
        bot.send_message(chat_id, "😕 Спочатку напиши /start, щоб отримати персонажа!")
        return

    # Випадково відповідаємо "Так" або "Ні"
    answer = random.choice(["✅ Так", "❌ Ні"])
    bot.send_message(chat_id, answer)

@bot.message_handler(func=lambda message: message.text.lower().startswith("я -"))
def guess_who(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.first_name

    if user_id not in players:
        bot.send_message(chat_id, "😕 Спочатку напиши /start, щоб отримати персонажа!")
        return

    guess = message.text[3:].strip()  # Беремо текст після "Я -"
    correct_character = players[user_id]

    if guess.lower() == correct_character.lower():
        scores[user_id] += 1  # Додаємо бал
        bot.send_message(chat_id, f"🎉 {username} вгадав! Це був {correct_character}! 🏆 Очки: {scores[user_id]}")
        del players[user_id]  # Видаляємо гравця після перемоги
    else:
        bot.send_message(chat_id, f"❌ {username}, це не {guess}. Продовжуй запитувати!")

@bot.message_handler(commands=['score'])
def show_score(message):
    """Показує рейтинг гравців."""
    if not scores:
        bot.send_message(message.chat.id, "Поки що ніхто не грав.")
        return

    ranking = "\n".join([f"{idx+1}. {scores[user]} очок" for idx, user in enumerate(sorted(scores, key=scores.get, reverse=True))])
    bot.send_message(message.chat.id, f"🏆 Таблиця рекордів:\n{ranking}")

bot.polling()
