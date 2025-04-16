from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ✅ 你的 LINE 金鑰
line_bot_api = LineBotApi('b3HrhXDjtJVCFZmCcgfwIIdaemUkeinzMZdFxbUsu1WC/ychBdhWbVb5fh91tAvRKns0N/42I2IkooAfP7YsHlH32qyGy+VvupMw3xsh7tdkYpdj8nCmq/6sGVzpl1gzsIs7eGscQCnHVJfASemdFwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ffc1cfa5f84c08d59253f4f34a835b28')

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reply = f"你的輸入是：{msg}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ✅ 最重要：讓 gunicorn 找到這個變數
app = app
