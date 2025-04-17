import os
from flask import Flask, request, abort
from line_bot_sdk import LineBotApi, WebhookHandler
from line_bot_sdk.exceptions import InvalidSignatureError
from analyzer import analyze_text_roadmap
import openai

# 設定金鑰
openai.api_key = "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"

app = Flask(__name__)

line_bot_api = LineBotApi('your_channel_access_token')
handler = WebhookHandler('your_channel_secret')

# 頻道配置
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    user_id = event.source.user_id
    
    # 分析發送的文字
    analysis_result = analyze_text_roadmap(text, user_id=user_id)
    
    # 回應用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=analysis_result)
    )

if __name__ == "__main__":
    app.run()
