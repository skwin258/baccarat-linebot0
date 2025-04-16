from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

from PIL import Image
import requests
from io import BytesIO
import os

app = Flask(__name__)

# ✅ 你的 LINE 金鑰
line_bot_api = LineBotApi('你的Channel Access Token')
handler = WebhookHandler('你的Channel Secret')

@app.route("/", methods=['GET'])
def home():
    return "你的百家樂分析機器人正在運作中！"

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

# ✅ 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reply = f"你的輸入是：{msg}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ✅ 處理圖片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    image = Image.open(BytesIO(message_content.content))
    save_path = f"received_{message_id}.jpg"
    image.save(save_path)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"已收到圖片，已儲存為 {save_path}")
    )

# ✅ gunicorn 用的 app 入口
app = app
