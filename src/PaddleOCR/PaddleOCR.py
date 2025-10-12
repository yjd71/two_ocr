
import logging

from paddleocr import PaddleOCR
import sys
import os


# 设置控制台编码为 UTF-8
if os.name == 'nt':
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    sys.stdout.reconfigure(encoding='utf-8')


# 关闭PaddleOCR的DEBUG日志
logger = logging.getLogger('ppocr')
logger.setLevel(logging.INFO)  # 设置INFO级别（可选：WARNING/ERROR）

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    use_doc_orientation_classify=False,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
    use_doc_unwarping=False,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
    use_textline_orientation=False,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
    lang="en",  # 通过 lang 参数来使用英文模型
    # device="gpu",  # 通过 device 参数使得在模型推理时使用 GPU
    # text_detection_model_dir="../../paddleocr/_pipelines"# 通过 text_detection_model_dir 指定本地模型路径
    # ocr_version="PP-OCRv4" # 通过 ocr_version 参数来使用 PP-OCR 其他版本
)

result = ocr.predict("../../Data/zhangqikui/test1/IMG_20250928_222538.jpg")
for res in result:
    # res.print()
    # print(res[1][0])
    res.save_to_img("output")
    res.save_to_json("output")
