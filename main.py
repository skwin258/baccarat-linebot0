from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "你的百家樂分析機器人正在運作中！"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
