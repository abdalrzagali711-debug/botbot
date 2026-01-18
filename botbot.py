import os, logging, requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# --- [ الإعدادات ] ---
TOKEN = "8149138526:AAHphePWqz3WdDM2NK16utIb0k-cJDK0iL4" 
MONGO_URL = "mongodb+srv://abdalrzagDB:10010207966##@cluster0.fighoyv.mongodb.net/?retryWrites=true&w=majority"
ADMIN_ID = 5524416062 # ضع الآيدي الخاص بك هنا

# --- [ قاعدة البيانات ] ---
client = MongoClient(MONGO_URL, tlsAllowInvalidCertificates=True)
db = client['EmpireBot_Ultimate']
users_col = db['users']

# --- [ سيرفر Flask للبقاء حياً ] ---
app = Flask('')
@app.route('/')
def home(): return "✅ Bot is Active!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

logging.basicConfig(level=logging.INFO)

# --- [ وظائف الرد على الأزرار ] ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # تسجيل المستخدم
    if not users_col.find_one({"user_id": user.id}):
        users_col.insert_one({"user_id": user.id, "name": user.first_name, "is_admin": False})
    
    keyboard = [
        [InlineKeyboardButton("📄 استخراج نصوص", callback_data='ocr'), 
         InlineKeyboardButton("📁 معالجة ملفات", callback_data='files')],
        [InlineKeyboardButton("🎬 قسم التحميل", callback_data='dl'), 
         InlineKeyboardButton("📊 إحصائياتي", callback_data='stats')]
    ]
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة التحكم", callback_data='admin_panel')])

    await update.message.reply_text(
        f"🚀 أهلاً بك يا {user.first_name}!\nالآن جميع الأزرار مفعلة. اختر الخدمة المطلوبة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # هذه الخطوة تجعل الزر يستجيب فوراً ويختفي مؤشر التحميل
    
    if query.data == 'ocr':
        await query.edit_message_text("📸 من فضلك أرسل الصورة التي تريد استخراج النص منها الآن.")
    elif query.data == 'files':
        await query.edit_message_text("📁 أرسل أي ملف (PDF, Doc, إلخ) وسأقوم بحفظه لك.")
    elif query.data == 'stats':
        total_users = users_col.count_documents({})
        await query.edit_message_text(f"📊 إحصائيات البوت:\n👥 عدد المستخدمين: {total_users}\n🆔 معرفك: {query.from_user.id}", parse_mode="Markdown")
    elif query.data == 'admin_panel':
        await query.edit_message_text("⚙️ لوحة التحكم:\nاستخدم /ban [ID] للحظر أو /broadcast للرسائل الجماعية.")

async def handle_uploads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("✅ استلمت الصورة. جاري تحليلها...")
    elif update.message.document:
        await update.message.reply_text(f"✅ تم استلام الملف: {update.message.document.file_name}")

# --- [ التشغيل ] ---
def main():
    Thread(target=run_flask).start()
    application = Application.builder().token(TOKEN).build()
    
    # ربط الأوامر والرسائل والأزرار بالمجيبات الخاصة بها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler)) # هذا هو المسؤول عن تفعيل الأزرار
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_uploads))
    
    print("🚀 البوت يعمل والأزرار مفعلة...")
    application.run_polling(drop_pending_updates=True)

if name == 'main':
    main()
