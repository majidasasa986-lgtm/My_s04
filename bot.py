import telebot
from telebot import types
from flask import Flask
import threading
import sqlite3
import datetime

# --- Render Keep-Alive (بیدار نگه داشتن ربات) ---
app = Flask('')

@app.route('/')
def home():
    return "s04piki AI System is Live!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

# --- تنظیمات اصلی ربات (Personalized for s04_1) ---
API_TOKEN = '8718138494:AAGEs59DOqu23gosOfltbIy379zTg5rgszU'
ADMIN_ID = 574341935  # آیدی عددی شما
ADMIN_USERNAME = "s04_1" # یوزنیم شما برای دکمه‌های تماس
bot = telebot.TeleBot(API_TOKEN)

# --- ایجاد پایگاه داده ---
def init_db():
    conn = sqlite3.connect('s04piki.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service TEXT, price TEXT, status TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- منوی اصلی (Turkish Menu) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🤖 AI Consultation"),
        types.KeyboardButton("💼 Order Services"),
        types.KeyboardButton("📊 My Orders"),
        types.KeyboardButton("💳 Pricing"),
        types.KeyboardButton("🧑‍💼 Contact Support"),
        types.KeyboardButton("🌐 Company Website")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "👋 s04piki AI Company desteğine hoş geldiniz!\n\n"
        "Geleceğin teknolojileriyle işinizi büyütelim. Lütfen yapmak istediğiniz işlemi panelden seçin."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu())

# --- بخش AI Consultation ---
@bot.message_handler(func=lambda m: m.text == "🤖 AI Consultation")
def ai_consult(message):
    msg = bot.send_message(message.chat.id, "🤖 Merhaba! Ben s04piki Akıllı Asistanı. İhtiyacınızı yazın، size en uygun çözümü ve fiyatı sunayım:")
    bot.register_next_step_handler(msg, ai_logic)

def ai_logic(message):
    text = message.text.lower()
    if "site" in text or "web" in text:
        res = "🌐 Harika! Web sitesi için 3 seçeneğimiz var: Landing Page ($30), Business ($80) veya E-ticaret ($150+). Detaylar için 'Order Services'e bakın."
    elif "bot" in text:
        res = "🤖 Telegram botları uzmanlık alanımız. $10'dan başlayan planlarımız mevcut. 'Order Services' üzerinden paketleri inceleyebilirsiniz."
    else:
        res = "🤖 Anlıyorum. Sizin için en akıllıca çözüm 'Standard' paketlerimiz olacaktır. Fiyatları görmek için menüyü kullanın."
    bot.send_message(message.chat.id, res)

# --- بخش Order Services ---
@bot.message_handler(func=lambda m: m.text == "💼 Order Services")
def order_categories(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Website Development", callback_data="cat_web"),
        types.InlineKeyboardButton("🤖 Telegram Bot", callback_data="cat_bot"),
        types.InlineKeyboardButton("📈 Social Media Automation", callback_data="cat_auto"),
        types.InlineKeyboardButton("🧠 AI Services", callback_data="cat_ai")
    )
    bot.send_message(message.chat.id, "Lütfen bir hizmet kategorisi seçin:", reply_markup=markup)

# --- پلن‌های روانشناسی فروش ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def show_plans(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    if call.data == "cat_bot":
        markup.add(types.InlineKeyboardButton("🟢 Basic Bot - $10", callback_data="buy_BasicBot_10"))
        markup.add(types.InlineKeyboardButton("🟡 Standard Bot - $25 ⭐ (En Popüler)", callback_data="buy_StdBot_25"))
        markup.add(types.InlineKeyboardButton("🔴 Advanced Bot - $60", callback_data="buy_AdvBot_60"))
        markup.add(types.InlineKeyboardButton("💀 AI Bot - $120", callback_data="buy_AIBot_120"))
        text = "🤖 Telegram Bot Paketleri:"
    elif call.data == "cat_web":
        markup.add(types.InlineKeyboardButton("🟢 Landing Page - $30", callback_data="buy_Landing_30"))
        markup.add(types.InlineKeyboardButton("🟡 Business Site - $80 ⭐", callback_data="buy_BusSite_80"))
        markup.add(types.InlineKeyboardButton("🔴 E-commerce - $150", callback_data="buy_Ecom_150"))
        text = "🌐 Web Sitesi Paketleri:"
    else:
        bot.send_message(call.message.chat.id, "Yakında eklenecek...")
        return
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- سیستم ثبت سفارش و پرداخت ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    bot.answer_callback_query(call.id)
    _, s_name, s_price = call.data.split('_')
    
    # ثبت در دیتابیس
    conn = sqlite3.connect('s04piki.db')
    cursor = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO orders (user_id, service, price, status, date) VALUES (?, ?, ?, ?, ?)", 
                   (call.from_user.id, s_name, s_price, "Pending", date))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    invoice = (
        f"📝 **Sipariş Özeti**\n\n"
        f"🛠 Servis: {s_name}\n"
        f"💰 Fiyat: ${s_price}\n"
        f"🆔 Takip ID: #{order_id}\n\n"
        "Ödemeyi onaylamak için lütfen aşağıdaki butonları kullanın:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Pay Now (Ödeme)", url=f"https://t.me/{ADMIN_USERNAME}"))
    markup.add(types.InlineKeyboardButton("📩 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}"))
    
    bot.send_message(call.message.chat.id, invoice, reply_markup=markup, parse_mode="Markdown")
    
    # خبر به ادمین (شما)
    bot.send_message(ADMIN_ID, f"📥 **YENİ SİPARİŞ!**\n\nUser: {call.from_user.id}\nServis: {s_name}\nFiyat: ${s_price}\nID: {order_id}")

# --- لیست سفارشات کاربر ---
@bot.message_handler(func=lambda m: m.text == "📊 My Orders")
def my_orders(message):
    conn = sqlite3.connect('s04piki.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, service, status FROM orders WHERE user_id = ?", (message.chat.id,))
    orders = cursor.fetchall()
    conn.close()

    if not orders:
        bot.send_message(message.chat.id, "Henüz bir siparişiniz bulunmuyor.")
    else:
        text = "📋 **Sipariş Geçmişiniz:**\n\n"
        for o in orders:
            text += f"ID: #{o[0]} | {o[1]} | Durum: {o[2]}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💳 Pricing")
def pricing(message):
    bot.send_message(message.chat.id, "💵 Tüm fiyatlarımız global pazar standartlarına göre belirlenmiştir. 'Order Services' kısmından güncel fiyatları görebilirsiniz.")

@bot.message_handler(func=lambda m: m.text == "🧑‍💼 Contact Support")
def support(message):
    bot.send_message(message.chat.id, f"🆘 Destek ve sorularınız için: @{ADMIN_USERNAME}")

@bot.message_handler(func=lambda m: m.text == "🌐 Company Website")
def website(message):
    bot.send_message(message.chat.id, "🔗 Web sitemizi ziyaret edin: www.s04piki.com")

# --- پایان و استارت ربات ---
bot.infinity_polling()
