def analyze_text_roadmap(text, simple=False):
    import re

    # 常見術語關鍵字查詢
    glossary_keywords = ["術語", "說明", "牌路"]
    if any(kw in text for kw in glossary_keywords):
        return (
            "📘 常見術語與牌路說明：\n"
            "\n🟥 莊家：代表色通常為紅色，點數高於閒家則莊勝。\n"
            "🟦 閒家：代表色通常為藍色，點數高於莊家則閒勝。\n"
            "🟩 和局：莊閒點數相同，俗稱『四婆』。\n"
            "💠 對子：首兩張牌為同點數，如莊對、閒對。\n"
            "👑 天生贏家：前兩張牌合為 8 或 9 點。\n"
            "💵 傭金：押莊贏通常需扣 5% 傭金。\n"
            "\n🔥 長龍：同一方連續多次獲勝。\n"
            "🔁 單跳：莊閒交錯出現。\n"
            "🔂 雙跳：莊莊閒閒、閒閒莊莊 等兩局為單位的跳動。\n"
            "🪃 拍黐：連續出現後換邊，如莊莊莊閒。\n"
            "🏠 隔黐：兩局一跳，莊莊閒莊莊閒。\n"
            "\n📌 可輸入：\n- 正常牌路：如『莊 閒 閒 莊 和』\n- 加入點數：如『莊6/3 9點 閒2/2/4 8點』\n- 查術語：輸入『術語』或『說明』\n- 簡版分析：輸入『簡單 莊 閒 閒 莊』\n- 若連閒達5次，會提示是否考慮反打"
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

    # 長龍判斷
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

    long_dragon = ""
    if max_streak >= 4:
        long_dragon = f"🔥 出現{streak_side}家長龍（連續 {max_streak} 次），建議可考慮追龍策略。\n"

    # 閒連續5次提示反打
    consecutive_player = 0
    for p in reversed(parts):
        if p == "閒":
            consecutive_player += 1
        else:
            break
    reverse_tip = ""
    if consecutive_player >= 5:
        reverse_tip = f"⚠️ 閒家已連閒 {consecutive_player} 次，是否考慮反打莊？\n"

    # 轉折偵測
    turns = 0
    for i in range(2, len(parts)):
        if parts[i] != parts[i - 1] and parts[i - 1] != parts[i - 2] and parts[i] != parts[i - 2]:
            turns += 1
    turn_info = f"🔁 目前牌路出現轉折次數：{turns} 次，代表近期走勢多變化。\n" if turns >= 2 else ""

    explanation = ""
    if banker_rate > player_rate:
        explanation = f"因本場牌局中，莊家出現次數較多（{banker_count} 次），代表莊家連貫性或趨勢較強。"
        if banker_pair > 0:
            explanation += f" 另外出現了 {banker_pair} 次莊對，增加莊家優勢的穩定性。"
    elif player_rate > banker_rate:
        explanation = f"因本場牌局中，閒家出現次數較多（{player_count} 次），代表閒家目前佔優。"
        if player_pair > 0:
            explanation += f" 同時出現了 {player_pair} 次閒對，也有利於閒家持續走勢。"
    else:
        explanation = "目前莊閒比例相近，尚無明顯趨勢可依。"

    # 點數分析補充
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
            detail_msg += f"\n📈 本局莊家牌力較強（{b_score} 比 {p_score}），優勢明顯。"
        elif p_score > b_score:
            detail_msg += f"\n📈 本局閒家牌力較強（{p_score} 比 {b_score}），優勢明顯。"
        else:
            detail_msg += f"\n⚖️ 本局為平點（{b_score} 比 {p_score}），視為和局。"

    msg = f"📊 模板分析結果：\n"
    msg += f"莊：{banker_count} 次\n閒：{player_count} 次\n和：{tie_count} 次\n幸運6：{lucky6_count} 次\n"
    msg += f"閒對:{player_pair}次\n莊對:{banker_pair}次\n"
    msg += f"\n莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n"
    msg += f"{suggestion}\n\n📌 {explanation}\n"
    msg += long_dragon
    msg += reverse_tip
    msg += turn_info
    msg += detail_msg or "\n更明確的分析請提供當場閒莊牌點數（例如：莊6/3 9點、閒2/2/4 8點）"
    return msg
