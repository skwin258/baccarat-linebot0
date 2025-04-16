from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

from PIL import Image
import requests
from io import BytesIO
import os

from analyzer import analyze_roadmap
from text_parser import parse_text_history

app = Flask(__name__)

# ✅ LINE 金鑰（請先確認是否已正確填入）
line_bot_api = LineBotApi('b3HrhXDjtJVCFZmCcgfwIIdaemUkeinzMZdFxbUsu1WC/ychBdhWbVb5fh91tAvRKns0N/42I2IkooAfP7YsHlH32qyGy+VvupMw3xsh7tdkYpdj8nCmq/6sGVzpl1gzsIs7eGscQCnHVJfASemdFwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ffc1cfa5f84c08d59253f4f34a835b28')

@app.route("/", methods=['GET'])
def home():
    return "百家樂分析機器人運作中"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Webhook URL OK"

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ✅ 處理文字指令（輸入莊 閒 閒 和）
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_input = event.message.text.strip()
    if all(c in ['莊', '閒', '和', ' ', 'x', 'X', '1','2','3','4','5','6','7','8','9','0'] for c in user_input):
        result = parse_text_history(user_input)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入最近局勢，例如：莊 閒 閒 和 莊")
        )

# ✅ 處理圖片分析（上傳牌路圖片）
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    image = Image.open(BytesIO(message_content.content))
    save_path = f"received_{message_id}.jpg"
    image.save(save_path)

    result = analyze_roadmap(save_path)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )

app = app
