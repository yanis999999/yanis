import telebot
from telebot import types
import requests
import json
import uuid
import os

BOT_TOKEN = "8430242777:AAF0INzXaCTFGtgVaImCnqkD8gmQ6WZDMnw" #توكنك ياغالي
droms = telebot.TeleBot(BOT_TOKEN)

iid = uuid.uuid4().hex.upper()

def D():
    url = "https://api.vulcanlabs.co/smith-auth/api/v1/token"
    payload = {
        "device_id": iid,
        "order_id": "",
        "product_id": "",
        "purchase_token": "",
        "subscription_id": ""
    }
    headers = {
        'User-Agent': "Chat Smith Android, Version 4.0.5(1032)",
        'Accept': "application/json",
        'Content-Type': "application/json",
        'x-vulcan-application-id': "com.smartwidgetlabs.chatgpt"
    }
    res = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return res.get("AccessToken")

def KARAR(token, php_code):
    prompt = f"""
    أنت مساعد برمجي متخصص. مهمتك: تحويل الكود المرسل من PHP إلى بايثون بدقة كاملة،
    مع الحفاظ على نفس الوظائف والمنطق. أرجو تقديم الكود النهائي جاهز للاستخدام في بايثون،
    بدون أي تغييرات في المنطق، وبتنسيق مرتب وواضح.

    الكود المرسل من المستخدم:
    ```php
    {php_code}
    ```
    """
    url = "https://api.vulcanlabs.co/smith-v2/api/v7/chat_android"
    payload = {
        "model": "gpt-4o-mini",
        "user": iid,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200000,
        "nsfw_check": True
    }
    headers = {
        'User-Agent': "Chat Smith Android, Version 4.0.5(1032)",
        'Accept': "application/json",
        'Content-Type': "application/json",
        'x-vulcan-application-id': "com.smartwidgetlabs.chatgpt",
        'authorization': f"Bearer {token}"
    }
    res = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return res["choices"][0]["Message"]["content"]

token = D()

@droms.message_handler(commands=['start'])
def welcome_message(message):
    c = types.InlineKeyboardButton('• Dev •', url='t.me/XV_YX')

    n = types.InlineKeyboardMarkup(row_width=2)
    n.add(c)
    droms.send_message(
        message.chat.id,
        """<strong>
👋🏻
-  -  -  -  -  -  -  -  -  -  -  -  -  -  -   -  -
اهلاً بك عـزيزي في بـوت 
تحـويل php الـى بايثـون 
فقط ارسل ملفـك واسـتمتع! 
</strong>""",
        reply_markup=n,
        parse_mode='html'
    )

@droms.message_handler(content_types=['document'])
def handle_file(message):
    file_info = droms.get_file(message.document.file_id)
    file_name = message.document.file_name

    if not file_name.endswith(".php"):
        droms.send_message(message.chat.id, "❌ الرجاء إرسال ملف PHP فقط!")
        return

    downloaded_file = droms.download_file(file_info.file_path)
    php_code = downloaded_file.decode("utf-8")

    droms.send_message(message.chat.id, "⏳ جاري تحويل الكود إلى بايثون، يرجى الانتظار...")

    try:
        python_code = KARAR(token, php_code)
        output_file_name = file_name.replace(".php", ".py")
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(python_code)

        with open(output_file_name, "rb") as f:
            l = types.InlineKeyboardButton('• Dev •', url='t.me/XV_YX')
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(l)
            droms.send_document(message.chat.id, f, caption='تم ✅', reply_markup=m)

        os.remove(output_file_name)
    except Exception as e:
        droms.send_message(message.chat.id, f"❌ حدث خطأ أثناء التحويل: {str(e)}")

droms.polling()