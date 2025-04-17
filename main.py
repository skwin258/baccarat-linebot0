from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, FlexSendMessage
import re
import os
import openai
from analyzer import analyze_text_roadmap, save_chart

app = Flask(__name__)

# LINE API 設定
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
    user_id = event.source.user_id
    simple = False

    if msg.lower() == '簡單版':
        simple = True
    elif msg.lower() == '專業版':
        simple = False

    # 關鍵字查詢
    response = analyze_text_roadmap(msg, simple=simple, user_id=user_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 處理圖片
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    save_path = f"received_{message_id}.jpg"
    with open(save_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    response = analyze_text_roadmap(save_path)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

# Flex message example
@handler.add(MessageEvent, message=TextMessage)
def handle_message_with_flex(event):
    msg = event.message.text
    if "分析圖表" in msg:
        # 假設用戶輸入要分析圖表
        seq = msg.split()  # 假設是用戶提供的最新牌局序列
        chart_url = save_chart(seq)
        flex_message = FlexSendMessage(
            alt_text='百家樂結果統計圖',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": chart_url,
                    "size": "full",
                    "aspectMode": "cover"
                }
            }
        )
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
