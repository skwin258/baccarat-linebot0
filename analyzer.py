def analyze_text_roadmap(text, simple=False):
    # 常見術語關鍵字查詢
    glossary_keywords = ["術語", "說明", "牌路"]
    if any(kw in text for kw in glossary_keywords):
        return (
            "📘 常見術語與牌路說明：\n"
            "\n🟥 莊家：代表色通常為紅色。勝出代表莊家點數大於閒家。\n"
            "🟦 閒家：代表色通常為藍色。勝出代表閒家點數大於莊家。\n"
            "🟩 和局：點數相同，俗稱四婆。\n"
            "💠 對子：拿到兩張相同牌（如莊對、閒對）。\n"
            "👑 天生贏家：兩張牌總和為8或9點，稱為天王牌。\n"
            "🚫 停叫：不補牌情況。\n"
            "💵 傭金：莊勝會抽5%佣金。\n"
            "\n🔥 長莊／長閒：連續開出莊或閒。\n"
            "🔁 單跳：莊閒交替出現，如莊閒莊閒。\n"
            "🔂 雙跳：莊莊閒閒，輪流出現兩局。\n"
            "🪃 拍黐：連開數次莊後出現閒，或反之。\n"
            "🏠 隔黐：兩閒一莊、兩莊一閒反覆。"
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

    # 轉折偵測
    turns = 0
    for i in range(2, len(parts)):
        if parts[i] != parts[i - 1] and parts[i - 1] != parts[i - 2] and parts[i] != parts[i - 2]:
            turns += 1
    turn_info = f"🔄 目前牌路出現轉折次數：{turns} 次，代表近期走勢多變化。\n" if turns >= 2 else ""

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

    msg = f"📊 模板分析結果：\n"
    msg += f"莊：{banker_count} 次\n閒：{player_count} 次\n和：{tie_count} 次\n幸運6：{lucky6_count} 次\n"
    msg += f"閒對:{player_pair}次\n莊對:{banker_pair}次\n"
    msg += f"\n莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n"
    msg += f"{suggestion}\n\n📌 {explanation}\n"
    msg += long_dragon
    msg += turn_info
    msg += "\n更明確的分析請提供當場閒莊牌點數如下\n莊6/3 9點 閒6/2 8點"
    return msg
