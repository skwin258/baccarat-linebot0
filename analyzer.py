import re
import openai
import matplotlib.pyplot as plt
import io
import base64
from tinydb import TinyDB, Query
from datetime import datetime

openai.api_key = "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"

# 🧠 雲端資料庫 (TinyDB 替代，可改為 Supabase/Firebase)
db = TinyDB('user_data.json')
user_history = {}

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

# 主分析函數
def analyze_text_roadmap(text, user_id=None):
    # 使用者歷史記錄
    if user_id:
        user_history.setdefault(user_id, [])
        user_history[user_id].append(text.strip())
        db.insert({"uid": user_id, "history": text.strip(), "time": datetime.now().isoformat()})

    # 開獎結果分析
    parts = text.strip().split()
    banker_count = parts.count("莊")
    player_count = parts.count("閒")
    tie_count = parts.count("和")
    lucky6_count = parts.count("6")

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    recommendation = "⚠️ 建議觀望，尚無明顯趨勢"
    if banker_rate >= 60:
        recommendation = f"✅ 建議押莊（勝率 {banker_rate}%）"
    elif player_rate >= 60:
        recommendation = f"✅ 建議押閒（勝率 {player_rate}%）"

    chart_url = save_chart(parts)

    msg = "\n🎯【百家樂專業分析】\n"
    msg += f"開莊：{banker_count} 次｜開閒：{player_count} 次｜和局：{tie_count}｜幸運6：{lucky6_count}\n"
    msg += f"莊勝率：{banker_rate}%｜閒勝率：{player_rate}%\n"
    msg += recommendation + "\n"
    msg += f"📈 圖表分析：\n<img src='{chart_url}' alt='趨勢圖' width='300' />"

    return msg
