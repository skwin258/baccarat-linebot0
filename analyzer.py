import re
import random
from datetime import datetime
import openai
import matplotlib.pyplot as plt
import io
import base64
from tinydb import TinyDB, Query

openai.api_key = "sk-你的key"

# 🧠 雲端資料庫 (TinyDB 替代，可改為 Supabase/Firebase)
db = TinyDB('user_data.json')
user_records = {}
user_history = {}
user_balance = {}

# 圖表分析函數
def save_chart(seq):
    banker = seq.count("莊")
    player = seq.count("閒")
    tie = seq.count("和")
    lucky = seq.count("6")

    labels = ['莊', '閒', '和', '幸運6']
    values = [banker, player, tie, lucky]

    plt.figure(figsize=(5, 3))
    plt.bar(labels, values)
    plt.title("百家樂結果統計圖")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{encoded}"

# GPT 模擬智能客服
def ask_gpt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是百家樂專家助理，擅長分析下注趨勢與操作建議，請用自然語言回應使用者。"},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ 無法取得分析：{str(e)}"

# 策略模擬回測（順勢追打）
def simulate_strategy(seq):
    profit = 0
    stake = 100
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            profit += stake * 0.95 if seq[i] == "莊" else stake
        else:
            profit -= stake
    return f"💸 策略模擬：連打順勢追擊結果 → {profit} 元"

# 主分析函數
def analyze_text_roadmap(text, simple=False, user_id=None):
    # GPT 自然語分析入口
    if not re.match(r"^[莊閒和6 ]{2,}$", text.strip()) and "點" not in text and not any(k in text for k in ["術語", "說明", "操作", "贏", "查帳"]):
        return ask_gpt(text)

    # 使用者歷史記錄
    if user_id:
        user_history.setdefault(user_id, [])
        if re.match(r"^[莊閒和6 ]{2,}$", text.strip()):
            user_history[user_id].append(text.strip())
            db.insert({"uid": user_id, "history": text.strip(), "time": datetime.now().isoformat()})
        if len(user_history[user_id]) > 10:
            user_history[user_id] = user_history[user_id][-10:]

    # 贏分記錄（今天我贏3000）
    if re.search(r"贏[\s]*([0-9]+)", text):
        amount = int(re.search(r"贏[\s]*([0-9]+)", text).group(1))
        user_balance[user_id] = {"amount": amount, "time": datetime.now().strftime("%m/%d %H:%M")}
        return f"🧾 已記錄 {amount} 元於 {user_balance[user_id]['time']}"

    if "查帳" in text and user_id in user_balance:
        return f"📒 你目前紀錄贏分為 {user_balance[user_id]['amount']} 元（{user_balance[user_id]['time']}）"

    # 開獎結果分析
    parts = text.strip().split()
    banker_count = parts.count("莊")
    player_count = parts.count("閒")
    tie_count = parts.count("和")
    lucky6_count = parts.count("6")

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    def describe_trend(seq):
        trends = []
        streak = 1
        switch_count = 0
        previous = seq[0]

        for i in range(1, len(seq)):
            if seq[i] == previous:
                streak += 1
            else:
                trends.append(f"{previous}x{streak}")
                switch_count += 1
                streak = 1
                previous = seq[i]
        trends.append(f"{previous}x{streak}")

        stability = "📐 穩定走勢" if max(streak for s in trends for streak in [int(s.split('x')[1])]) >= 3 else "📐 震盪盤"
        return "📊 走勢：「{}」\n{}".format(" → ".join(trends), stability)

    recommendation = "⚠️ 建議觀望，尚無明顯趨勢"
    if banker_rate >= 60:
        recommendation = f"✅ 建議押莊（勝率 {banker_rate}%）"
    elif player_rate >= 60:
        recommendation = f"✅ 建議押閒（勝率 {player_rate}%）"

    chart_url = save_chart(parts)
    simulate = simulate_strategy(parts)

    msg = "\n🎯【百家樂專業分析】\n"
    msg += f"開莊：{banker_count} 次｜開閒：{player_count} 次｜和局：{tie_count}｜幸運6：{lucky6_count}\n"
    msg += f"莊勝率：{banker_rate}%｜閒勝率：{player_rate}%\n"
    msg += recommendation + "\n"
    msg += describe_trend(parts) + "\n"
    msg += simulate + "\n"
    msg += f"📈 圖表分析：\n<img src='{chart_url}' alt='趨勢圖' width='300' />"

    return msg
