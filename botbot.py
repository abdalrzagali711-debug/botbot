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
db = client['EmpireBot_Ultra']
users_col = db['users']

# --- [ سيرفر Flask ] ---
app = Flask('')
@app.route('/')
def home(): return "✅ Empire Bot Ultra is Live!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

logging.basicConfig(level=logging.INFO)

# --- [ معالجة النصوص والملفات ] ---

async def handle_docs_and_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # تحقق من الحظر
    user = users_col.find_one({"user_id": user_id})
    if user and user.get("is_banned"): return

    if update.message.photo:
        await update.message.reply_text("🔎 جاري تحليل الصورة واستخراج النصوص منها...")
        # هنا يمكنك دمج API خارجي لاستخراج النص أو معالجة محلية
        await update.message.reply_text("✅ (تجريبي) تم استلام الصورة، خاصية OCR قيد الربط بـ API.")
    
    elif update.message.document:
        await update.message.reply_text(f"📁 تم استلام الملف: {update.message.document.file_name}")

# --- [ أوامر الإدارة الشاملة ] ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = users_col.find_one({"user_id": user.id})
    
    if not u_data:
        users_col.insert_one({"user_id": user.id, "name": user.first_name, "is_admin": False, "is_banned": False})

    key = [
        [InlineKeyboardButton("🎬 تحميل", callback_data='dl'), InlineKeyboardButton("📄 استخراج نصوص", callback_data='ocr')],
        [InlineKeyboardButton("🤖 ذكاء اصطناعي", callback_data='ai'), InlineKeyboardButton("📊 إحصائياتي", callback_data='stats')]
    ]
    if user.id == ADMIN_ID or (u_data and u_data.get("is_admin")):
        key.append([InlineKeyboardButton("⚙️ لوحة التحكم الشاملة", callback_data='admin_main')])

    await update.message.reply_text(f"🔥 مرحباً بك في الإمبراطورية V3\nأرسل ملفات، صور، أو روابط للبدء!", reply_markup=InlineKeyboardMarkup(key))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    total = users_col.count_documents({})
    txt = f"⚙️ لوحة التحكم\n\n👥 الأعضاء: {total}\n\nالأوامر:\n/ban [ID] - حظر\n/unban [ID] - فك حظر\n/promote [ID] - ترقية"
    await query.edit_message_text(txt, parse_mode="Markdown")

# --- [ التشغيل النهائي ] ---

def main():
    Thread(target=run_flask).start()
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern='admin_main'))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_docs_and_photos))
    
    print("🚀 Empire Bot Ultra V3 Started!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()