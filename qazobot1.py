import telebot
from telebot import types
import sqlite3
import datetime

bot = telebot.TeleBot('6907256543:AAFlJSj4KJiTkCBwSMF7i9hcplAVcCo3jfY')

# hafta kunlar
uzbek_weekdays = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]

# Ma'lumot baza
def init_db():
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS qazo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        namoz TEXT,
        date TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Qazo ma'lumotlari bazada mavjudligini tekshirish
def is_qazo_exists(user_id, namoz, date):
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM qazo WHERE user_id = ? AND namoz = ? AND date = ?', (user_id, namoz, date))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Qazo ma'lumotlarini bazaga saqlash
def save_qazo_to_db(user_id, namoz, date):
    if not is_qazo_exists(user_id, namoz, date):
        conn = sqlite3.connect('qazo_namoz.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO qazo (user_id, namoz, date) VALUES (?, ?, ?)', (user_id, namoz, date))
        conn.commit()
        conn.close()
        return True
    return False

# Foydalanuvchi qazolarini bazadan olish
def get_qazos_from_db(user_id):
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT namoz, date FROM qazo WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

# Bazadan qazo o'chirish
def delete_qazo_from_db(user_id, date, namoz):
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM qazo WHERE user_id = ? AND date = ? AND namoz = ?', (user_id, date, namoz))
    conn.commit()
    conn.close()

# Hafta kunini olish funksiyasi
def get_uzbek_weekday(date):
    return uzbek_weekdays[date.weekday()]

# Qazo namoz tugmalarini yaratish
def create_qazo_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🕌 Bomdod", "🕌 Peshin", "🕌 Asr")
    markup.row("🕌 Shom", "🕌 Xufton", "🕌 Vitr")
    markup.row("🔙 Ortga")
    return markup

# Bosh menyu
def main_menu(is_admin=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Qazo Qo'shish", "📜 Qazo Namozlarim")
    markup.row("📦 Arxiv Qo'shish", "💬 Taklif yoki Muammo")
    if is_admin:
        markup.row("✉️ Xabar")
    return markup

# Botni ishga tushirish va yangi foydalanuvchini adminga xabar berish
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    is_admin = user_id == 6903661947  # Admin ID
    bot.send_message(user_id, "🕌 Assalomu alaykum! Qazo namozlaringizni qo'shish  uchun tugmalardan foydalaning.", reply_markup=main_menu(is_admin))

    # Yangi foydalanuvchi qo'shilganida adminga xabar
    admin_chat_id = 6903661947
    bot.send_message(admin_chat_id, f"Yangi foydalanuvchi qo'shildi: tg://openmessage?user_id={user_id}")

# Qazo Qo'shish bo'limi
@bot.message_handler(func=lambda message: message.text == "➕ Qazo Qo'shish")
def qazo_qoshish(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Qaysi namozni qazo qilganingizni tanlang.", reply_markup=create_qazo_buttons())

# Namoz tanlanganda qazo saqlash
# Namoz tanlanganda qazo saqlash
@bot.message_handler(func=lambda message: message.text in ["🕌 Bomdod", "🕌 Peshin", "🕌 Asr", "🕌 Shom", "🕌 Xufton", "🕌 Vitr"])
def save_qazo(message):
    user_id = message.chat.id
    namoz = message.text
    today = datetime.datetime.now()
    today_str = str(today.date())
    weekday = get_uzbek_weekday(today)  # Haftaning kunini olish
    
    if save_qazo_to_db(user_id, namoz, today_str):
        bot.send_message(user_id, f"Siz {weekday} ({today_str}) sanasida {namoz} namozini qazo qildingiz.")
    else:
        bot.send_message(user_id, f"Roʻyxatda bor!")

# Qazo Namozlarim qismini yaratish va o'zbek tilidagi hafta kunlarini ko'rsatish
@bot.message_handler(func=lambda message: message.text == "📜 Qazo Namozlarim")
def show_qazo_list(message):
    user_id = message.chat.id
    qazolar = get_qazos_from_db(user_id)
    
    if qazolar:
        msg = "Siz quyidagi namozlarni qazo qilgansiz:\n"
        for idx, (namoz, date) in enumerate(qazolar):
            weekday = get_uzbek_weekday(datetime.datetime.strptime(date, "%Y-%m-%d"))
            msg += f"{idx+1}. {weekday} ({date}) kuni - {namoz}\n"
        msg += "--------------------------------------------------------------------------------------------------- O'qilgan namozni o'chirish uchun kerakli raqamni yuboring."
        bot.send_message(user_id, msg, reply_markup=delete_menu())
    else:
        bot.send_message(user_id, "Sizda qazo namozlari yo'q.")

# O'chirish menyusi
def delete_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Ortga")
    return markup

# O'qilgan qazoni o'chirish
@bot.message_handler(func=lambda message: message.text.isdigit())
def delete_qazo_by_index(message):
    user_id = message.chat.id
    index = int(message.text) - 1

    qazolar = get_qazos_from_db(user_id)
    if 0 <= index < len(qazolar):
        namoz, date = qazolar[index]
        delete_qazo_from_db(user_id, date, namoz)
        bot.send_message(user_id, f"{date} sanasidagi {namoz} qazo namozi o'chirildi.")
    else:
        bot.send_message(user_id, "Noto'g'ri raqam kiritildi.")

# Taklif yoki muammo bo'limi va adminga xabar yuborish
@bot.message_handler(func=lambda message: message.text == "💬 Taklif yoki Muammo")
def suggestion_section(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Ortga")  # Ortga tugmasini qo'shamiz
    bot.send_message(message.chat.id, "Taklif (muammoingiz)ni kiriting va bizga yuboring yoki_________________ '🔙 Ortga' _____________tugmasini bosing.", reply_markup=markup)
    bot.register_next_step_handler(message, handle_suggestion)

def handle_suggestion(message):
    if message.text == "🔙 Ortga":
        # Foydalanuvchi ortga qaytdi, adminga hech qanday xabar yuborilmaydi
        bot.send_message(message.chat.id, "Ortga qaytdingiz.", reply_markup=main_menu())
    else:
        # Foydalanuvchi xabar kiritdi, taklif yoki muammo adminga yuboriladi
        send_suggestion(message)

def send_suggestion(message):
    suggestion = message.text
    admin_chat_id = 6903661947  # Adminning chat ID'sini kiriting
    bot.send_message(admin_chat_id, f"Yangi taklif yoki muammo: tg://openmessage?user_id={message.chat.id}\n\n{suggestion}")
    bot.send_message(message.chat.id, "Taklifingiz yoki muammoingiz yuborildi! Rahmat 😊", reply_markup=main_menu())

# Ortga qaytish
@bot.message_handler(func=lambda message: message.text == "🔙 Ortga")
def go_back(message):
    user_id = message.chat.id
    is_admin = user_id == 6903661947
    bot.send_message(message.chat.id, "Ortga qaytdingiz.", reply_markup=main_menu(is_admin))

# Arxiv Qo'shish bo'limi
@bot.message_handler(func=lambda message: message.text == "📦 Arxiv Qo'shish")
def archive_section(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("1 kun oldin", "2 kun oldin")
    markup.row("3 kun oldin", "4 kun oldin")
    markup.row("🔙 Ortga")
    bot.send_message(message.chat.id, "Necha kun oldingi namozni kiritmoqchisiz?", reply_markup=markup)

# Arxivdan kun tanlanganda namoz tanlash
@bot.message_handler(func=lambda message: message.text in ["1 kun oldin", "2 kun oldin", "3 kun oldin", "4 kun oldin"])
def archive_namaz_select(message):
    user_id = message.chat.id
    days_ago = int(message.text.split()[0])  # Masalan "1 kun oldin" -> 1
    today = datetime.datetime.now().date()
    selected_date = today - datetime.timedelta(days=days_ago)
    bot.send_message(user_id, f"{selected_date} sanasi uchun qaysi namozni kiritmoqchisiz?", reply_markup=create_qazo_buttons())

    # Tanlangan sana va namozni saqlash uchun keyingi qadam
    bot.register_next_step_handler(message, lambda m: save_archive_qazo(m, selected_date))

# Arxiv namozni saqlash
def save_archive_qazo(message, selected_date):
    user_id = message.chat.id
    namoz = message.text

    if namoz in ["🕌 Bomdod", "🕌 Peshin", "🕌 Asr", "🕌 Shom", "🕌 Xufton", "🕌 Vitr"]:
        if save_qazo_to_db(user_id, namoz, str(selected_date)):
            bot.send_message(user_id, f"Siz {selected_date} sanasida {namoz} namozini qazo qilganingizni kiritdingiz.")
        else:
            bot.send_message(user_id, f"Roʻyxatda bor!")
    else:
        bot.send_message(user_id, "Noto'g'ri namoz tanlandi. Iltimos, qaytadan urinib ko'ring.")

    # Qazo saqlangandan so'ng bosh menyuga qaytish
    is_admin = user_id == 6903661947  # Admin ID
    bot.send_message(user_id, "Siz bosh menyudasiz.", reply_markup=main_menu(is_admin))

# Xabar bo'limi
@bot.message_handler(func=lambda message: message.text == "✉️ Xabar")
def message_section(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("✉️ Ommaviy Xabar", "📩 Shaxsiy Xabar", "🔙 Ortga")
    bot.send_message(user_id, "Xabar yuborish usulini tanlang:", reply_markup=markup)

# Ommaviy xabar yuborish
@bot.message_handler(func=lambda message: message.text == "✉️ Ommaviy Xabar")
def send_mass_message(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Ortga")
    bot.send_message(user_id, "Ommaviy xabar yuborish uchun matnni kiriting yoki '🔙 Ortga' tugmasini bosing:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_mass_message)

def handle_mass_message(message):
    if message.text == "🔙 Ortga":
        bot.send_message(message.chat.id, "Ortga qaytdingiz.", reply_markup=main_menu(is_admin=True))
    else:
        send_mass_message_handler(message)

def send_mass_message_handler(message):
    mass_message = message.text
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT user_id FROM qazo')
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    for user_id in user_ids:
        try:
            bot.send_message(user_id, mass_message)
        except Exception as e:
            print(f"Xatolik: {e}")

    bot.send_message(message.chat.id, "Xabar hammaga yuborildi.", reply_markup=main_menu(is_admin=True))

# Shaxsiy xabar yuborish
@bot.message_handler(func=lambda message: message.text == "📩 Shaxsiy Xabar")
def send_private_message(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔙 Ortga")
    bot.send_message(user_id, "Foydalanuvchi ID'sini kiriting yoki '🔙 Ortga' tugmasini bosing:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_private_message)

def handle_private_message(message):
    if message.text == "🔙 Ortga":
        bot.send_message(message.chat.id, "Ortga qaytdingiz.", reply_markup=main_menu(is_admin=True))
    else:
        send_private_message_handler(message)

def send_private_message_handler(message):
    target_user_id = message.text
    conn = sqlite3.connect('qazo_namoz.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM qazo WHERE user_id = ?', (target_user_id,))
    user_exists = cursor.fetchone()
    conn.close()

    if user_exists:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🔙 Ortga")
        bot.send_message(message.chat.id, "Yuboriladigan xabarni kiriting yoki '🔙 Ortga' tugmasini bosing:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: send_private_message_to_user(msg, target_user_id))
    else:
        bot.send_message(message.chat.id, "Bu ID botda mavjud emas. Iltimos, boshqa ID kiriting yoki '🔙 Ortga' tugmasini bosing.", reply_markup=delete_menu())

def send_private_message_to_user(message, target_user_id):
    if message.text == "🔙 Ortga":
        bot.send_message(message.chat.id, "Ortga qaytdingiz.", reply_markup=main_menu(is_admin=True))
    else:
        private_message = message.text
        try:
            bot.send_message(target_user_id, private_message)
            bot.send_message(message.chat.id, "Xabar muvaffaqiyatli yuborildi!", reply_markup=main_menu(is_admin=True))
        except Exception as e:
            bot.send_message(message.chat.id, f"Xabar yuborishda xatolik: {e}")
# Botni ishga tushirish
if __name__ == '__main__':
    init_db()
    bot.polling(none_stop=True)