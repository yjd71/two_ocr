import os
import cv2
import numpy as np
from datetime import datetime
from paddleocr import PaddleOCR, draw_ocr  # draw_ocr 用于把结果画到图像上（跨版本兼容性请见下方）

img_path = "../../Data/zhangqikui/test1/IMG_20250928_222538.jpg"
img = cv2.imread(img_path)  # BGR uint8

# --------- 示例预处理（替换为你的实际预处理链） ----------
# 示例：缩放 + CLAHE 增强（灰度） + 转回 BGR
h, w = img.shape[:2]
new_w = 1024
scale = new_w / w
img_resized = cv2.resize(img, (new_w, int(h * scale)), interpolation=cv2.INTER_LINEAR)

# CLAHE（增强对比度）示例
gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
gray_clahe = clahe.apply(gray)
preprocessed = cv2.cvtColor(gray_clahe, cv2.COLOR_GRAY2BGR)  # back to BGR uint8
# -------------------------------------------------------------

# debug：确保确实修改了像素
cv2.imwrite("debug_preprocessed.png", preprocessed)

# 初始化 OCR（和你原来的一样）
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
)

# 将 ndarray 直接传给 OCR（大多数 paddleocr 版本支持 ndarray）
try:
    result = ocr.predict(preprocessed)   # 有些版本用 predict
except Exception:
    try:
        result = ocr.ocr(preprocessed, cls=False)  # 兼容旧版 API
    except Exception as e:
        raise RuntimeError("OCR 调用失败，检查 paddleocr 版本与输入类型。错误: " + str(e))

# 把识别结果画回到你预处理后的图像并保存（确保结果可视化是基于预处理图）
boxes, texts, scores = [], [], []
# 不同版本返回的结构不同，下面尝试兼容解析 result
if isinstance(result, dict):
    # 若返回 dict（罕见），直接保存 json 或按 dict 结构解析
    import json
    out_json = f"ocr_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
else:
    # 通常 result 是 list of [box, (text, score)] 或者 list of lines
    for item in result:
        # 兼容两种常见结构
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            box = item[0]
            txt = None
            score = None
            # item[1] 可能是 (text, score) 或者 [text, score]
            if isinstance(item[1], (list, tuple)) and len(item[1]) >= 2:
                txt = item[1][0]
                score = item[1][1]
            elif isinstance(item[1], str):
                txt = item[1]
            boxes.append(box)
            texts.append(txt if txt is not None else "")
            scores.append(score if score is not None else 0.0)

    # 使用 paddleocr 提供的 draw_ocr（如果可用）把结果渲染在 preprocessed 上
    try:
        img_with_boxes = draw_ocr(preprocessed, boxes, texts, scores)
        out_path = f"ocr_on_preprocessed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(out_path, img_with_boxes)
        print("已保存可视化结果：", out_path)
    except Exception:
        # 如果 draw_ocr 不可用，可手工画框（简单版）
        vis = preprocessed.copy()
        for b in boxes:
            pts = np.array(b, dtype=np.int32).reshape((-1,1,2))
            cv2.polylines(vis, [pts], True, (0,255,0), 2)
        out_path = f"ocr_on_preprocessed_basic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(out_path, vis)
        print("已保存基础可视化结果：", out_path)
