from flask import Flask, request, abort
import openai
import json
import re
from analyzer import analyze_text_roadmap
import logging

# 初始化 Flask 應用
app = Flask(__name__)

# 設置 OpenAI API 金鑰
openai.api_key = "sk-你的key"

# 設置日誌
logging.basicConfig(level=logging.INFO)

# LINE Bot Webhook URL
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 取得 LINE 訊息
        body = request.get_data(as_text=True)
        print(f"Request body: {body}")  # 輸出接收到的請求，方便調試

        # 解析收到的訊息
        if "events" in body:
            events = json.loads(body).get("events", [])
            for event in events:
                user_message = event.get("message", {}).get("text", "").strip()

                # 確保訊息存在且不為空
                if user_message:
                    response_message = analyze_text_roadmap(user_message)
                    # 發送回應訊息至 LINE
                    send_line_message(event["replyToken"], response_message)
                else:
                    print("Received empty message.")
                    
        return 'OK', 200
    except Exception as e:
        # 如果有錯誤，記錄錯誤訊息
        logging.error(f"Error processing the webhook: {e}")
        return 'Error', 500

# 發送 LINE 訊息的函數
def send_line_message(reply_token, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + '你的LINE BOT Channel Access Token'
    }

    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }

    # 發送 POST 請求至 LINE API 回傳訊息
    try:
        response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)
        if response.status_code != 200:
            logging.error(f"Error sending message: {response.text}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# 啟動 Flask 伺服器
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
