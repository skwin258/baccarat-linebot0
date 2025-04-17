import re
import random
from datetime import datetime
import openai

openai.api_key = "sk-你的key"

user_records = {}
user_history = {}


def ask_gpt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是百家樂專家，擅長解釋投注策略與走勢分析，請用簡單口語風格回覆玩家問題。"},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ 無法取得分析：{str(e)}"


def analyze_text_roadmap(text, simple=False, user_id=None):
    # 若非格式明確指令，交給 GPT 回覆
    if not re.match(r"^[莊閒和6 ]{2,}$", text.strip()) and "點" not in text and not any(k in text for k in ["術語", "說明", "操作", "贏"]):
        return ask_gpt(text)

    # ✨ 玩家歷史儲存處理
    if user_id:
        user_history.setdefault(user_id, [])
        if re.match(r"^[莊閒和6 ]{2,}$", text.strip()):
            user_history[user_id].append(text.strip())
        if len(user_history[user_id]) > 5:
            user_history[user_id] = user_history[user_id][-5:]

    def describe_trend(seq):
        if len(seq) < 4:
            return "📈 目前牌路尚短，建議多觀察幾局再入場。"

        trends = []
        streak = 1
        switch_count = 0
        previous = seq[0]
        last_streak = []

        for i in range(1, len(seq)):
            if seq[i] == previous:
                streak += 1
            else:
                if streak >= 3:
                    trends.append(f"連開{previous} {streak} 次")
                elif streak == 2:
                    trends.append(f"{previous}連莊")
                else:
                    trends.append(f"{previous}短打")
                switch_count += 1
                last_streak.append(previous)
                streak = 1
                previous = seq[i]

        if streak >= 3:
            trends.append(f"連開{previous} {streak} 次")
        elif streak == 2:
            trends.append(f"{previous}連莊")
        else:
            trends.append(f"{previous}短打")
        last_streak.append(previous)

        stable_ratio = sum(1 for t in trends if "連" in t) / len(trends)
        stability = "📐 走勢偏穩定，較適合順勢操作。" if stable_ratio >= 0.6 else "📐 走勢偏震盪，建議觀望或短打應對。"

        tug_war = switch_count >= len(seq) // 2 and all(len(s) <= 2 for s in trends)
        tug_war_msg = "🤼 目前屬纏鬥盤，莊閒激烈交錯，下注建議採用停看聽策略。" if tug_war else ""

        return "📊 走勢觀察：" + "，".join(trends) + "。\n" + stability + ("\n" + tug_war_msg if tug_war_msg else "")

    if "術語" in text:
        return (
            "📘 常見術語與牌路說明：\n\n"
            "🟥 莊家：代表色通常為紅色，點數高於閒家則莊勝。\n"
            "🟦 閒家：代表色通常為藍色，點數高於莊家則閒勝。\n"
            "🟩 和局：莊閒點數相同，俗稱『四婆』。\n"
            "💠 對子：首兩張牌為同點數，如莊對、閒對。\n"
            "👑 天生贏家：前兩張牌合為 8 或 9 點。\n"
            "💵 傭金：押莊贏通常需扣 5% 傭金。\n"
            "🔥 長龍：同一方連續多次獲勝。\n"
            "🔁 單跳：莊閒交錯出現。\n"
            "🔂 雙跳：莊莊閒閒、閒閒莊莊 等兩局為單位的跳動。\n"
            "🪃 拍黐：連續出現後換邊，如莊莊莊閒。\n"
            "🏠 隔黐：兩局一跳，莊莊閒莊莊閒。"
        )

    if any(k in text for k in ["說明", "怎麼用", "操作"]):
        return (
            "📗 操作說明：\n"
            "分析下場牌路請輸入：如『莊 閒 閒 莊 和』前10場結果\n"
            "加入當場牌型點數分析更加準確：如『莊6/3 9點 閒2/2/4 8點』\n"
            "查術語：輸入『百家樂術語』\n"
            "簡單版分析：輸入『簡單版』\n"
            "專業版分析：輸入『專業版』"
        )

    if user_id and re.search(r"贏[\s:]*\d+", text):
        win_amount = re.search(r"贏[\s:]*([0-9]+)", text)
        if win_amount:
            amount = int(win_amount.group(1))
            now = datetime.now().strftime("%m/%d %H:%M")
            user_records[user_id] = {"amount": amount, "time": now}
            return f"✅ {now} 已為你紀錄本日贏分：{amount} 元"

    if user_id and "目前贏" in text:
        record = user_records.get(user_id)
        if record:
            return f"🧾 你在 {record['time']} 所紀錄贏分為 {record['amount']} 元"
        return "尚未紀錄，請先輸入『今天我贏3000』這類語句。"

    if text.strip() == "分析紀錄":
        history = user_history.get(user_id, [])
        if not history:
            return "🕹 尚無分析紀錄，請先輸入幾組走勢。"
        return "🧠 最近分析紀錄：\n" + "\n".join(history)

    if re.search(r"[?？]", text):
        if "下" in text:
            return "📌 請輸入最近10局結果（如：莊 閒 閒 莊 閒 閒 莊）我幫你分析要不要下。"
        elif "怎麼操作" in text or "怎麼用" in text:
            return "📘 輸入『說明』查看所有功能。"

    parts = text.strip().split()
    banker_count = parts.count("莊")
    player_count = parts.count("閒")
    tie_count = parts.count("和")
    lucky6_count = parts.count("6")

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    banker_points = re.search(r"莊[\d/]+\s*(\d+)點", text)
    player_points = re.search(r"閒[\d/]+\s*(\d+)點", text)

    detail_msg = ""
    if banker_points and player_points:
        b = int(banker_points.group(1))
        p = int(player_points.group(1))
        winner = "莊" if b > p else "閒" if p > b else "和局"
        detail_msg = f"🔍 本局結果：莊 {b} 點 vs 閒 {p} 點 → {winner} 勝"

    explanation = describe_trend(parts)

    recommendation = "⚠️ 建議觀望，尚無明顯趨勢"
    if banker_rate >= 60:
        recommendation = f"✅ 莊家連貫性較強，目前勝率 {banker_rate}%，可考慮押莊。"
    elif player_rate >= 60:
        recommendation = f"✅ 閒家連貫性較強，目前勝率 {player_rate}%，可考慮押閒。"

    msg = "\n🎯【百家樂專業分析】\n"
    msg += f"開莊：{banker_count} 次｜開閒：{player_count} 次｜和局：{tie_count}｜幸運6：{lucky6_count}\n"
    msg += f"莊勝率：{banker_rate}%｜閒勝率：{player_rate}%\n"
    msg += recommendation + "\n"
    msg += explanation + "\n"
    msg += detail_msg
    return msg
