import os
import subprocess
import threading
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8523083737:AAEsO3w-fFbOLT8wRhaItPjb86xA1zEwaj0"

# مجلد التخزين
UPLOAD_FOLDER = "user_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاموس لتخزين العمليات النشطة
active_processes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **بوت استضافة ملفات بايثون**\n\n"
        "📁 **الأوامر:**\n"
        "/upload - رفع ملف بايثون\n"
        "/list - عرض الملفات\n"
        "/run <اسم الملف> - تشغيل ملف\n"
        "/stop <اسم الملف> - إيقاف ملف\n"
        "/delete <اسم الملف> - حذف ملف\n"
        "/status - حالة الملفات النشطة"
    )

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 أرسل ملف بايثون (.py) الآن:")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    
    if document.file_name.endswith('.py'):
        # تحميل الملف
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(UPLOAD_FOLDER, document.file_name)
        
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"✅ تم رفع الملف: {document.file_name}")
    else:
        await update.message.reply_text("❌ يرجى رفع ملف بايثون فقط (.py)")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.py')]
    
    if files:
        file_list = "\n".join(files)
        await update.message.reply_text(f"📁 الملفات المتاحة:\n{file_list}")
    else:
        await update.message.reply_text("❌ لا توجد ملفات")

async def run_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ استخدم: /run <اسم الملف>")
        return
    
    filename = context.args[0]
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        await update.message.reply_text("❌ الملف غير موجود")
        return
    
    if filename in active_processes:
        await update.message.reply_text("⚠️ الملف يعمل بالفعل")
        return
    
    # تشغيل الملف بدون وقت محدود
    def run_script():
        try:
            process = subprocess.Popen(
                ['python', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            active_processes[filename] = process
            
            # انتظار الانتهاء (بدون timeout)
            stdout, stderr = process.communicate()
            
            # تسجيل النتيجة
            if stdout:
                logger.info(f"إخراج {filename}: {stdout[:1000]}")
            if stderr:
                logger.error(f"أخطاء {filename}: {stderr[:1000]}")
                
        except Exception as e:
            logger.error(f"خطأ في {filename}: {e}")
        finally:
            # إزالة من القائمة عند الانتهاء
            if filename in active_processes:
                del active_processes[filename]
    
    thread = threading.Thread(target=run_script)
    thread.daemon = True
    thread.start()
    
    await update.message.reply_text(f"🚀 بدأ تشغيل: {filename}")

async def stop_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ استخدم: /stop <اسم الملف>")
        return
    
    filename = context.args[0]
    
    if filename in active_processes:
        process = active_processes[filename]
        try:
            process.terminate()  # إيقاف العملية
            process.wait(timeout=5)  # انتظار الإيقاف
        except:
            process.kill()  # إجبار الإيقاف إذا لم يستجب
        
        del active_processes[filename]
        await update.message.reply_text(f"⏹️ تم إيقاف: {filename}")
    else:
        await update.message.reply_text("❌ الملف غير نشط")

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ استخدم: /delete <اسم الملف>")
        return
    
    filename = context.args[0]
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        # إيقاف الملف إذا كان نشطاً
        if filename in active_processes:
            await stop_file(update, context)
        
        os.remove(file_path)
        await update.message.reply_text(f"🗑️ تم حذف: {filename}")
    else:
        await update.message.reply_text("❌ الملف غير موجود")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if active_processes:
        active_list = "\n".join([f"{name} (🟢 نشط)" for name in active_processes.keys()])
        await update.message.reply_text(f"📊 الملفات النشطة:\n{active_list}")
    else:
        await update.message.reply_text("🔴 لا توجد ملفات نشطة")

async def restart_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ استخدم: /restart <اسم الملف>")
        return
    
    filename = context.args[0]
    
    # إيقاف ثم تشغيل
    if filename in active_processes:
        await stop_file(update, context)
    
    await run_file(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload_file))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("run", run_file))
    app.add_handler(CommandHandler("stop", stop_file))
    app.add_handler(CommandHandler("restart", restart_file))
    app.add_handler(CommandHandler("delete", delete_file))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("🤖 بوت الاستضافة يعمل بدون وقت محدود...")
    app.run_polling()

if __name__ == "__main__":
    main()