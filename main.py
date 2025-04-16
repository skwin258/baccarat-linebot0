from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from io import BytesIO
from PIL import Image
import pytesseract

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

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 取得圖片內容
    message_content = line_bot_api.get_message_content(event.message.id)
    img = Image.open(BytesIO(message_content.content))

    # 執行 OCR 辨識（使用繁體中文 + 英文）
    text = pytesseract.image_to_string(img, lang='chi_tra+eng')

    # 回傳辨識結果（下一步可分析下注建議）
    reply = f"辨識結果如下：\n{text.strip() or '（未偵測到文字）'}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ✅ 最重要：讓 gunicorn 找到這個變數
app = app
