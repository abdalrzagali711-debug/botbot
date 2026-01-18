import os, logging, requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- [ الإعدادات ] ---
TOKEN = "8149138526:AAHphePWqz3WdDM2NK16utIb0k-cJDK0iL4" 
MONGO_URL = "mongodb+srv://abdalrzagDB:10010207966##@cluster0.fighoyv.mongodb.net/?retryWrites=true&w=majority"
ADMIN_ID = 5524416062 # ضع الآيدي الخاص بك

# --- [ الاتصال بقاعدة البيانات ] ---
client = MongoClient(MONGO_URL, tlsAllowInvalidCertificates=True)
db = client['EmpireBot_Mega']
users_col = db['users']

# --- [ نظام Flask للبقاء حياً ] ---
app = Flask('')
@app.route('/')
def home(): return "✅ Empire Mega Bot is Running!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

logging.basicConfig(level=logging.INFO)

# --- [ وظائف الخدمات ] ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # تسجيل المستخدم
    if not users_col.find_one({"user_id": user.id}):
        users_col.insert_one({"user_id": user.id, "name": user.first_name, "is_admin": False, "is_banned": False})
    
    keyboard = [
        [InlineKeyboardButton("📄 استخراج نصوص", callback_data='ocr'), InlineKeyboardButton("📁 معالجة ملفات", callback_data='files')],
        [InlineKeyboardButton("🎬 قسم التحميل", callback_data='dl'), InlineKeyboardButton("📊 إحصائياتي", callback_data='stats')]
    ]
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data='admin_main')])

    await update.message.reply_text(f"🚀 أهلاً بك في بوت الخدمات الشاملة!\nأرسل لي صورة لاستخراج النص أو ملفاً لمعالجته.", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("💡 استلمت الصورة! جاري تفعيل نظام OCR لاستخراج النصوص...")
    elif update.message.document:
        await update.message.reply_text(f"📁 استلمت الملف: {update.message.document.file_name}\nجاري الحفظ في السحابة...")

# --- [ تشغيل البوت ] ---
def main():
    Thread(target=run_flask).start()
    # drop_pending_updates=True ضرورية جداً لحل خطأ Conflict الذي في صورك
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_media))
    
    print("🚀 البوت انطلق...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
