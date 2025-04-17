def analyze_text_roadmap(text, simple=False):
    import re

    # 問答模式：獨立思考回應
    if re.search(r"[?？]", text):
        if "莊" in text or "閒" in text:
            return f"🤖 你想問：{text}\n目前建議：請輸入近期牌路以供分析。"
        else:
            return "🤖 我是百家樂分析助手，可輸入牌路、點數、下注或詢問術語。例：『莊 閒 莊』、『莊6/3 9點 閒2/2/4 8點』、或輸入『術語』了解更多。"

    # 指令式切換模式
    if text.startswith("#模式"):
        mode = text.split()[-1]
        return f"✅ 模式已設定為「{mode}」，後續將優先分析『{mode}』走勢。"

    # 模擬下注功能
    if "押" in text and ("莊" in text or "閒" in text):
        side = "莊" if "莊" in text else "閒"
        stake = re.search(r"(押\d+)", text)
        stake_txt = stake.group(1) if stake else "下注"
        # 未知分析時的預設回應
        return f"🎯 你選擇 {stake_txt} 在 {side}。
請提供最近牌路（如『莊 閒 閒 莊』），讓我幫你看看是否合理！"

    # 常見術語查詢
    glossary_keywords = ["術語", "說明", "牌路"]
    if any(kw in text for kw in glossary_keywords):
        return (
            "📘 常見術語與牌路說明：\n"
            "\n🟥 莊家：點數高於閒家則莊勝。🟦 閒家：點數高於莊家則閒勝。\n"
            "🟩 和局：點數相同。💠 對子：拿到兩張相同牌。👑 天牌：兩張加總為 8 或 9。\n"
            "\n🔥 長龍：同方連開多局。🔁 單跳：莊閒交錯。🔂 雙跳：莊莊閒閒等。\n"
            "🪃 拍黐：長莊中斷換閒。🏠 隔黐：莊莊閒、閒閒莊。\n"
            "\n📌 也可輸入：\n- 正常牌路：『莊 閒 閒 莊』\n- 點數格式：『莊6/3 9點 閒2/2/4 8點』\n- 模擬下注：『押100在莊』\n- 模式切換：『#模式 單跳』"
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
        return f"莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n{suggestion}"

    # 長龍偵測
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

    long_dragon = f"🔥 出現{streak_side}家長龍（連續 {max_streak} 次），建議可考慮追龍策略。\n" if max_streak >= 4 else ""

    # 閒連續提示反打
    consecutive_player = 0
    for p in reversed(parts):
        if p == "閒":
            consecutive_player += 1
        else:
            break
    reverse_tip = f"⚠️ 閒家已連閒 {consecutive_player} 次，是否考慮反打莊？\n" if consecutive_player >= 5 else ""

    # 轉折偵測
    turns = 0
    for i in range(2, len(parts)):
        if parts[i] != parts[i - 1] and parts[i - 1] != parts[i - 2] and parts[i] != parts[i - 2]:
            turns += 1
    turn_info = f"🔁 目前牌路出現轉折次數：{turns} 次，代表近期走勢多變化。\n" if turns >= 2 else ""

    # 解釋趨勢
    explanation = ""
    if banker_rate > player_rate:
        explanation = f"因本場莊家開出較多（{banker_count} 次），趨勢偏向莊家。"
        if banker_pair > 0:
            explanation += f" 同時出現 {banker_pair} 次莊對，莊家穩定性高。"
    elif player_rate > banker_rate:
        explanation = f"因本場閒家開出較多（{player_count} 次），趨勢偏向閒家。"
        if player_pair > 0:
            explanation += f" 且出現 {player_pair} 次閒對，有延續趨勢可能。"
    else:
        explanation = "莊閒開出次數相近，目前無明顯趨勢。"

    # 點數分析
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
