from PIL import Image
import cv2
import numpy as np

def analyze_roadmap(image_path):
    # 這是模擬分析，實際你可以加上 OCR 或圖像處理邏輯
    print(f"分析圖片：{image_path}")
    
    # 假資料 - 可根據實際圖片內容做真實分析
    result = {
        "莊": 14,
        "閒": 10,
        "和": 2,
        "莊勝率": round(14 / (14 + 10 + 2) * 100, 2),
        "閒勝率": round(10 / (14 + 10 + 2) * 100, 2),
        "建議": "⚠️ 建議觀望，無明顯趨勢"
    }
    return result
