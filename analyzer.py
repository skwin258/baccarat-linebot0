import cv2
import numpy as np
import os

TEMPLATE_DIR = "templates"
TEMPLATES = {
    "banker": "banker.png",
    "player": "player.png",
    "tie": "tie.png",
    "lucky6": "lucky6.png",

    "banker_banker_pair": "banker_banker_pair.png",
    "banker_player_pair": "banker_player_pair.png",
    "banker_mixed_pair": "banker_mixed_pair.png",

    "player_banker_pair": "player_banker_pair.png",
    "player_player_pair": "player_player_pair.png",
    "player_mixed_pair": "player_mixed_pair.png",

    "tie_banker_pair": "tie_banker_pair.png",
    "tie_player_pair": "tie_player_pair.png",
    "tie_mixed_pair": "tie_mixed_pair.png",

    "lucky6_banker_pair": "lucky6_banker_pair.png",
    "lucky6_player_pair": "lucky6_player_pair.png",
    "lucky6_mixed_pair": "lucky6_mixed_pair.png",
}

def match_template(image, template_path, threshold=0.7):
    template_orig = cv2.imread(template_path, 0)
    if template_orig is None:
        print(f"❌ 模板讀取失敗：{template_path}")
        return 0

    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    count_total = 0
    for scale in [0.90, 0.95, 1.0, 1.05, 1.10]:  # 更寬鬆的縮放範圍
        try:
            template = cv2.resize(template_orig, None, fx=scale, fy=scale)
            if img_gray.shape[0] < template.shape[0] or img_gray.shape[1] < template.shape[1]:
                continue
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            count_total += len(list(zip(*loc[::-1])))
        except Exception as e:
            print(f"⚠️ 模板比對錯誤：{template_path}, 錯誤：{e}")

    return count_total

def analyze_roadmap(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return "❌ 圖片讀取失敗，請再傳一次。"

    result_count = {key: 0 for key in TEMPLATES.keys()}

    for name, filename in TEMPLATES.items():
        template_path = os.path.join(TEMPLATE_DIR, filename)
        if not os.path.exists(template_path):
            print(f"❌ 模板不存在：{template_path}")
            continue
        count = match_template(image, template_path)
        result_count[name] = count

    # 整合出現次數
    banker_total = sum(result_count[k] for k in result_count if k.startswith("banker") and not k.startswith("banker_"))
    player_total = sum(result_count[k] for k in result_count if k.startswith("player") and not k.startswith("player_"))
    tie_total = sum(result_count[k] for k in result_count if k.startswith("tie") and not k.startswith("tie_"))
    lucky6_total = sum(result_count[k] for k in result_count if k.startswith("lucky6") and not k.startswith("lucky6_"))

    total = banker_total + player_total
    banker_rate = round(banker_total / total * 100, 2) if total else 0
    player_rate = round(player_total / total * 100, 2) if total else 0

    if banker_rate >= 60:
        suggestion = f"✅ 建議下注莊家（勝率 {banker_rate}%）"
    elif player_rate >= 60:
        suggestion = f"✅ 建議下注閒家（勝率 {player_rate}%）"
    else:
        suggestion = f"⚠️ 建議觀望，目前無明顯趨勢"

    msg = f"📊 模板分析結果：\n"
    msg += f"莊：{banker_total} 次\n閒：{player_total} 次\n和：{tie_total} 次\n幸運6：{lucky6_total} 次\n"
    msg += f"莊勝率：{banker_rate}%\n閒勝率：{player_rate}%\n"
    msg += suggestion
    return msg
