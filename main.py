from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

from PIL import Image
import requests
from io import BytesIO
import os
import cv2
import numpy as np

from analyzer import analyze_roadmap  # 導入分析模組

app = Flask(__name__)

# ✅ 你的 LINE 金鑰（已填入）
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

# ✅ 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reply = f"你的輸入是：{msg}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ✅ 偵測莊對與閒對小點

def detect_pair_symbols(image_path):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 紅色（莊對）
    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1)

    # 藍色（閒對）
    blue_lower = np.array([100, 100, 100])
    blue_upper = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

    red_count = cv2.countNonZero(red_mask)
    blue_count = cv2.countNonZero(blue_mask)

    return red_count, blue_count

# ✅ 處理圖片訊息，並進行分析
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    image = Image.open(BytesIO(message_content.content))
    save_path = f"received_{message_id}.jpg"
    image.save(save_path)

    # 呼叫分析模組，取得結果
    result = analyze_roadmap(save_path)

    # 偵測莊對/閒對小點
    red_pair_count, blue_pair_count = detect_pair_symbols(save_path)

    # 整理回覆訊息
    response = f"牌路分析結果：\n"
    response += f"莊：{result['莊']} 次\n閒：{result['閒']} 次\n和：{result['和']} 次\n"
    response += f"莊勝率：{result['莊勝率']}%\n閒勝率：{result['閒勝率']}%\n"
    response += f"莊對出現次數：{red_pair_count} 次\n閒對出現次數：{blue_pair_count} 次\n"
    response += result['建議']

    # 回傳 LINE 訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

# ✅ gunicorn 找入口用
app = app
