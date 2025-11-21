import os
import subprocess
import sys
import psutil
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8523083737:AAEsO3w-fFbOLT8wRhaItPjb86xA1zEwaj0"
ADMIN_ID = 7125289523
active_bots = {}

def is_admin(user_id):
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("البوت الرئيسي جاهز لتشغيل البوتات الأخرى")

async def run_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("يرجى تحديد اسم ملف البوت\nاستخدام: /run filename.py")
        return
    
    filename = context.args[0]
    
    if not os.path.exists(filename):
        await update.message.reply_text(f"الملف {filename} غير موجود")
        return
    
    if filename in active_bots:
        await update.message.reply_text(f"البوت {filename} يعمل بالفعل")
        return
    
    try:
        process = subprocess.Popen([sys.executable, filename])
        active_bots[filename] = process
        await update.message.reply_text(f"تم تشغيل البوت: {filename}")
    except Exception as e:
        await update.message.reply_text(f"خطأ في تشغيل البوت: {str(e)}")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("يرجى تحديد اسم ملف البوت\nاستخدام: /stop filename.py")
        return
    
    filename = context.args[0]
    
    if filename not in active_bots:
        await update.message.reply_text(f"البوت {filename} غير نشط")
        return
    
    try:
        process = active_bots[filename]
        process.terminate()
        process.wait()
        del active_bots[filename]
        await update.message.reply_text(f"تم إيقاف البوت: {filename}")
    except Exception as e:
        await update.message.reply_text(f"خطأ في إيقاف البوت: {str(e)}")

async def list_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not active_bots:
        await update.message.reply_text("لا توجد بوتات نشطة")
        return
    
    bot_list = "\n".join([f"• {bot}" for bot in active_bots.keys()])
    await update.message.reply_text(f"البوتات النشطة:\n{bot_list}")

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("يرجى تحديد اسم ملف البوت\nاستخدام: /restart filename.py")
        return
    
    filename = context.args[0]
    
    if filename in active_bots:
        process = active_bots[filename]
        process.terminate()
        process.wait()
        del active_bots[filename]
    
    try:
        process = subprocess.Popen([sys.executable, filename])
        active_bots[filename] = process
        await update.message.reply_text(f"تم إعادة تشغيل البوت: {filename}")
    except Exception as e:
        await update.message.reply_text(f"خطأ في إعادة تشغيل البوت: {str(e)}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    panel_text = """
🎛️ لوحة الأدمن

الأوامر المتاحة:
/run filename.py - تشغيل بوت
/stop filename.py - إيقاف بوت  
/restart filename.py - إعادة تشغيل بوت
/list - عرض البوتات النشطة
/panel - عرض هذه اللوحة
/stats - إحصائيات النظام
/killall - إيقاف جميع البوتات
"""
    await update.message.reply_text(panel_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    active_count = len(active_bots)
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    stats_text = f"""
📊 إحصائيات النظام

البوتات النشطة: {active_count}
استخدام المعالج: {cpu_percent}%
الذاكرة المستخدمة: {memory.percent}%
المسخدم: @XV_YX
"""
    await update.message.reply_text(stats_text)

async def killall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not active_bots:
        await update.message.reply_text("لا توجد بوتات نشطة")
        return
    
    stopped_count = 0
    for filename, process in list(active_bots.items()):
        try:
            process.terminate()
            process.wait()
            del active_bots[filename]
            stopped_count += 1
        except Exception as e:
            continue
    
    await update.message.reply_text(f"تم إيقاف {stopped_count} بوت")

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("يرجى تحديد اسم ملف البوت\nاستخدام: /status filename.py")
        return
    
    filename = context.args[0]
    
    if filename in active_bots:
        process = active_bots[filename]
        status = "نشط" if process.poll() is None else "متوقف"
        await update.message.reply_text(f"حالة البوت {filename}: {status}")
    else:
        await update.message.reply_text(f"البوت {filename} غير موجود في القائمة النشطة")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_bot))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("list", list_bots))
    app.add_handler(CommandHandler("restart", restart_bot))
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("killall", killall))
    app.add_handler(CommandHandler("status", bot_status))
    
    print("البوت الرئيسي يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()