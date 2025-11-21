import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت الخاص بك
BOT_TOKEN = "8430242777:AAF0INzXaCTFGtgVaImCnqkD8gmQ6WZDMnw"

# أمر البدء /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"مرحباً {user.mention_html()}! 👋\n"
        f"البوت يعمل بنجاح! ✅\n\n"
        f"الأوامر المتاحة:\n"
        f"/start - بدء التشغيل\n"
        f"/help - المساعدة\n"
        f"/test - اختبار البوت\n"
        f"/info - معلومات عن المستخدم"
    )

# أمر المساعدة /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **قائمة الأوامر:**

/start - بدء التشغيل
/help - عرض هذه الرسالة
/test - اختبار استجابة البوت
/info - معلومات المستخدم

🔹 يمكنك أيضاً إرسال أي رسالة وسأرد بنفس النص!
    """
    await update.message.reply_text(help_text)

# أمر الاختبار /test
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يعمل بشكل صحيح! الاستضافة نشطة.")

# أمر المعلومات /info
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    info_text = f"""
👤 **معلومات المستخدم:**
- الاسم: {user.first_name} {user.last_name or ''}
- المعرف: @{user.username or 'لا يوجد'}
- ID: {user.id}

💬 **معلومات الدردشة:**
- نوع الدردشة: {chat.type}
- ID الدردشة: {chat.id}
    """
    await update.message.reply_text(info_text)

# معالجة الرسائل النصية العادية
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"📨 تلقيت رسالتك: {user_message}")

# معالجة الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"حدث خطأ: {context.error}")

# الدالة الرئيسية
def main():
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    print("🤖 البوت يعمل الآن...")
    print("اضغط Ctrl+C لإيقاف البوت")
    
    application.run_polling()

if __name__ == "__main__":
    main()