from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from analyzer import analyze_text_roadmap

app = Flask(__name__)

# ✅ 請替換為你的 LINE 金鑰與密鑰
line_bot_api = LineBotApi('b3HrhXDjtJVCFZmCcgfwIIdaemUkeinzMZdFxbUsu1WC/ychBdhWbVb5fh91tAvRKns0N/42I2IkooAfP7YsHlH32qyGy+VvupMw3xsh7tdkYpdj8nCmq/6sGVzpl1gzsIs7eGscQCnHVJfASemdFwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ffc1cfa5f84c08d59253f4f34a835b28')

@app.route("/", methods=['GET'])
def index():
    return "你的百家樂分析 LINE 機器人運作中！"

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()

    # 玩家使用「簡單」關鍵字只顯示勝率建議
    if "簡單" in user_input:
        result = analyze_text_roadmap(user_input.replace("簡單", ""), simple=True)
    else:
        result = analyze_text_roadmap(user_input)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )

if __name__ == "__main__":
    app.run(debug=True)
