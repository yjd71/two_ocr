import logging
from paddleocr import PaddleOCR

# 关闭PaddleOCR的DEBUG日志
logger = logging.getLogger('ppocr')
logger.setLevel(logging.INFO)  # 设置INFO级别（可选：WARNING/ERROR）

# 初始化OCR模型（默认中英文模型）
ocr = PaddleOCR(
    # use_angle_cls=True,
    lang='en',
#     use_gpu=True,
)

image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'

result = ocr.predict(image)

for line in result[0]:
    # coordinates = line[0]
    text = line[1][0]
    # confidence = line[1][1]
    print(f"文本: {text}")
