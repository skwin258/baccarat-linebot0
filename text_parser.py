import re

def parse_text_history(text):
    # 將使用者輸入清理成 ['莊', '閒', '閒', '和'] 格式
    pattern = re.findall(r'(莊|閒|和)(x\d+)?', text)
    sequence = []
    for symbol, count in pattern:
        if count:
            n = int(count[1:])
            sequence.extend([symbol] * n)
        else:
            sequence.append(symbol)

    banker_count = sequence.count("莊")
    player_count = sequence.count("閒")
    tie_count = sequence.count("和")

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    if banker_rate >= 60:
        suggestion = f"✅ 建議下注莊家（勝率 {banker_rate}%）"
    elif player_rate >= 60:
        suggestion = f"✅ 建議下注閒家（勝率 {player_rate}%）"
    else:
        suggestion = "⚠️ 建議觀望，目前無明顯趨勢"

    return f"📊 文字分析：\n莊：{banker_count} 次\n閒：{player_count} 次\n和：{tie_count} 次\n莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n{suggestion}"
