import cv2
import numpy as np

def analyze_roadmap(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ 圖片讀取失敗，請再傳一次。"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    banker_count, player_count, tie_count = 0, 0, 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 10 < w < 60 and 10 < h < 60:
            roi = img[y:y+h, x:x+w]
            mean_color = cv2.mean(roi)[:3]

            if mean_color[2] > 150 and mean_color[0] < 100:  # 紅 → 莊
                banker_count += 1
            elif mean_color[0] > 150 and mean_color[2] < 100:  # 藍 → 閒
                player_count += 1
            elif mean_color[1] > 130:  # 綠 → 和
                tie_count += 1

    total = banker_count + player_count
    banker_rate = round(banker_count / total * 100, 2) if total else 0
    player_rate = round(player_count / total * 100, 2) if total else 0

    if banker_rate >= 60:
        suggestion = f"✅ 建議下注莊家（勝率 {banker_rate}%）"
    elif player_rate >= 60:
        suggestion = f"✅ 建議下注閒家（勝率 {player_rate}%）"
    else:
        suggestion = f"⚠️ 建議觀望，目前無明顯趨勢"

    return f"📊 圖像分析：\n莊：{banker_count} 次\n閒：{player_count} 次\n和：{tie_count} 次\n莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n{suggestion}"
