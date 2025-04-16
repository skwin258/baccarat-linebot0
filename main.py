from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ✅ 你的 LINE 金鑰
line_bot_api = LineBotApi('b3HrhXDtjJVCFZmCgfwlIdaemUkeinZMzdFxbUsul1kC/ychBdhWbVb5fh91tAvRKn s0N/4l2Z1KooAFP7YsH1H32qyGy+VvupMw3xsh7tdkYpdj8nCmq/6sGVzpl1gzsI s7eGsQCnHV9FA5emdFwdB04tB9/10/w1cDnyi1FU=')
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
