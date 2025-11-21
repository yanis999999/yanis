import os
import subprocess
import sys
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
    await update.message.reply_text("البوت جاهز للرفع")

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
    
    bot_list = "\n".join(active_bots.keys())
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
"""
    await update.message.reply_text(panel_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    active_count = len(active_bots)
    stats_text = f"""
📊 إحصائيات النظام

البوتات النشطة: {active_count}
المسخدم: @XV_YX
"""
    await update.message.reply_text(stats_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_bot))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("list", list_bots))
    app.add_handler(CommandHandler("restart", restart_bot))
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CommandHandler("stats", stats))
    
    print("البوت الرئيسي يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()