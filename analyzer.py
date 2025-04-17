import re

def analyze_text_roadmap(text, simple=False):
    # ✅ 問句偵測：啟用獨立思考回應
    if re.search(r"[?？]", text):
        if "莊" in text or "閒" in text:
            return f"🤖 你想問：{text}\n目前建議：請輸入最近牌路以供分析。"
        else:
            return "🤖 我是百家樂分析助手，可輸入牌路、點數、下注或詢問術語。例：『莊 閒 閒 莊』、『莊6/3 9點 閒2/2/4 8點』、或輸入『術語』了解更多。"

    # ✅ 模擬下注功能
    if "押" in text and ("莊" in text or "閒" in text):
        side = "莊" if "莊" in text else "閒"
        stake = re.search(r"押(\d+)", text)
        stake_txt = stake.group(1) if stake else "下注"
        return f"🎯 你選擇押 {stake_txt} 在 {side}。\n請提供最近牌路（如『莊 閒 閒 莊』），我會告訴你下注是否合理！"

    # ✅ 指令式模式切換
    if text.startswith("#模式"):
        mode = text.split()[-1]
        return f"✅ 模式已設定為「{mode}」，後續將優先分析『{mode}』風格。"

    # ✅ 術語與說明查詢
    glossary_keywords = ["術語", "說明", "牌路"]
    if any(kw in text for kw in glossary_keywords):
        return (
            "📘 常見術語與牌路說明：\n"
            "🟥 莊家：代表色紅，點數大於閒家則勝。\n"
            "🟦 閒家：代表色藍，點數大於莊家則勝。\n"
            "🟩 和局：點數相同（四婆）。\n"
            "💠 對子：莊或閒拿到兩張相同牌。\n"
            "👑 天牌：頭兩張牌為 8 或 9 點。\n"
            "🚫 停叫：不再補牌。💵 傭金：押莊贏需付 5% 抽水。\n"
            "🔥 長龍：莊或閒連開。🔁 單跳：莊閒交錯。🔂 雙跳：莊莊閒閒等。\n"
            "🪃 拍黐：連開莊後開閒或反之。🏠 隔黐：兩莊一閒反覆。\n"
            "\n📌 你也可以：\n- 模擬下注（例：押100在莊）\n- 指令切換分析風格（例：#模式 追龍）"
        )

    parts = text.strip().split()
    banker_count = parts.count("莊")
    player_count = parts.count("閒")
    tie_count = parts.count("和")
    lucky6_count = parts.count("6")

    banker_pair = sum("莊對" in p for p in parts)
    player_pair = sum("閒對" in p for p in parts)

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    suggestion = "⚠️ 建議觀望，目前無明顯趨勢"
    if len(parts) >= 4:
        if parts[-1] != parts[-2]:
            if parts[-1] == "莊":
                suggestion = f"✅ 目前走大路單跳，下場建議莊（勝率 {banker_rate}%）"
            elif parts[-1] == "閒":
                suggestion = f"✅ 目前走大路單跳，下場建議閒（勝率 {player_rate}%）"
        elif parts[-1] == parts[-2]:
            if parts[-1] == "莊":
                suggestion = f"✅ 莊家連莊中，建議續押莊（勝率 {banker_rate}%）"
            elif parts[-1] == "閒":
                suggestion = f"✅ 閒家連閒中，建議續押閒（勝率 {player_rate}%）"

    if simple:
        msg = f"莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n{suggestion}"
        return msg

    # 長龍分析
    max_streak = 1
    current_streak = 1
    streak_side = None
    for i in range(1, len(parts)):
        if parts[i] == parts[i - 1] and parts[i] in ["莊", "閒"]:
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
                streak_side = parts[i]
        else:
            current_streak = 1

    long_dragon = f"🔥 出現{streak_side}家長龍（連續 {max_streak} 次），可考慮追龍策略。\n" if max_streak >= 4 else ""

    # 閒連續提醒反打
    consecutive_player = 0
    for p in reversed(parts):
        if p == "閒":
            consecutive_player += 1
        else:
            break
    reverse_tip = f"⚠️ 閒家已連閒 {consecutive_player} 次，是否考慮反打莊？\n" if consecutive_player >= 5 else ""

    # 轉折次數
    turns = 0
    for i in range(2, len(parts)):
        if parts[i] != parts[i - 1] and parts[i - 1] != parts[i - 2] and parts[i] != parts[i - 2]:
            turns += 1
    turn_info = f"🔄 最近出現 {turns} 次轉折，表示走勢變化頻繁。\n" if turns >= 2 else ""

    # 解釋趨勢與勝率
    explanation = ""
    if banker_rate > player_rate:
        explanation = f"莊家開出次數較多（{banker_count} 次），偏向莊。"
        if banker_pair > 0:
            explanation += f" 且莊對次數為 {banker_pair}，增加穩定性。"
    elif player_rate > banker_rate:
        explanation = f"閒家開出次數較多（{player_count} 次），偏向閒。"
        if player_pair > 0:
            explanation += f" 且閒對次數為 {player_pair}，可續押。"
    else:
        explanation = "莊閒比例接近，目前趨勢不明。"

    # 點數解析
    detail_msg = ""
    banker_points = re.search(r"莊[\d/]+\s*(\d+)點", text)
    player_points = re.search(r"閒[\d/]+\s*(\d+)點", text)
    b_score = p_score = None
    if banker_points:
        b_score = int(banker_points.group(1))
        detail_msg += f"\n🔍 莊家點數：{banker_points.group(0)}"
    if player_points:
        p_score = int(player_points.group(1))
        detail_msg += f"\n🔍 閒家點數：{player_points.group(0)}"
    if b_score is not None and p_score is not None:
        if b_score > p_score:
            detail_msg += f"\n📈 莊家牌力勝（{b_score} 比 {p_score}）"
        elif p_score > b_score:
            detail_msg += f"\n📈 閒家牌力勝（{p_score} 比 {b_score}）"
        else:
            detail_msg += f"\n⚖️ 雙方點數相同，視為和局"

    msg = f"📊 模板分析結果：\n"
    msg += f"莊：{banker_count} 次\n閒：{player_count} 次\n和：{tie_count} 次\n幸運6：{lucky6_count} 次\n"
    msg += f"閒對:{player_pair}次\n莊對:{banker_pair}次\n"
    msg += f"\n莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n"
    msg += f"{suggestion}\n\n📌 {explanation}\n"
    msg += long_dragon
    msg += reverse_tip
    msg += turn_info
    msg += detail_msg or "\n📩 若要更精確分析，請輸入本局莊閒牌點數，如：莊6/3 9點 閒2/2/4 8點"
    return msg
