from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/')
def home():
    return 'Line Bot is running!'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'Webhook OK (GET)'
    elif request.method == 'POST':
        return 'Webhook OK (POST)'
    else:
        abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
