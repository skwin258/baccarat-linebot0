import cv2
import numpy as np

def analyze_roadmap(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {
            "莊": 0, "閒": 0, "和": 0,
            "莊勝率": 0.0, "閒勝率": 0.0,
            "建議": "無法讀取圖片，請重新上傳清晰的牌路圖。"
        }

    # 圖像預處理（轉灰階 + 模糊）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)

    # 偵測紅/藍/綠圓圈 (簡單統計用)
    red = cv2.inRange(image, (0, 0, 130), (100, 100, 255))
    blue = cv2.inRange(image, (130, 0, 0), (255, 100, 100))
    green = cv2.inRange(image, (0, 130, 0), (100, 255, 100))

    count_banker = cv2.countNonZero(red) // 100
    count_player = cv2.countNonZero(blue) // 100
    count_tie = cv2.countNonZero(green) // 100

    total = count_banker + count_player
    win_rate_banker = round(count_banker / total * 100, 2) if total else 0
    win_rate_player = round(count_player / total * 100, 2) if total else 0

    if win_rate_banker > 60:
        advice = "建議下注『莊』！近期偏莊。"
    elif win_rate_player > 60:
        advice = "建議下注『閒』！近期偏閒。"
    else:
        advice = "目前無明顯趨勢，建議觀望一局。"

    return {
        "莊": count_banker,
        "閒": count_player,
        "和": count_tie,
        "莊勝率": win_rate_banker,
        "閒勝率": win_rate_player,
        "建議": advice
    }
