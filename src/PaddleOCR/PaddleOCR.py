import logging

import aiofiles
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import sys
import os

from src.PaddleOCR.utils.load_img import load_img
from src.PaddleOCR.utils.preprocess_img import preprocess_img_pro

# 设置控制台编码为 UTF-8
if os.name == 'nt':
    import msvcrt

    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    sys.stdout.reconfigure(encoding='utf-8')

# 关闭PaddleOCR的DEBUG日志
logger = logging.getLogger('ppocr')
logger.setLevel(logging.INFO)  # 设置INFO级别（可选：WARNING/ERROR）


# 使用PaddleOCR识别
def ocr_recognition(image):
    # 初始化 ocr 引擎
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_server_det",
        text_recognition_model_name="PP-OCRv5_server_rec",
        use_doc_orientation_classify=False,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
        use_doc_unwarping=False,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
        use_textline_orientation=False,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
        # lang="en",  # 通过 lang 参数来使用英文模型
        # device="gpu",  # 通过 device 参数使得在模型推理时使用 GPU
        # text_detection_model_dir="../../paddleocr/_pipelines"# 通过 text_detection_model_dir 指定本地模型路径
        # ocr_version="PP-OCRv4" # 通过 ocr_version 参数来使用 PP-OCR 其他版本
    )

    result = ocr.predict(image)

    """
       保存识别结果的图片和json数据
    """
    for res in result:
        # res.print()
        print(res["rec_texts"])
        # res.save_to_img("output")
        # res.save_to_json("output")

    return result


# ocr调用函数
def paddle_ocr(image, preprocessed_image_save_path=None):
    # 加载图片
    original_image = load_img(image)
    # 图片预处理
    preprocessed_image = preprocess_img_pro(original_image)

    # # 构建文件保存
    # preprocessed_image_save = Image.fromarray(preprocessed_image)  # 转换为 PIL 图像
    # preprocessed_image_save.save(preprocessed_image_save_path)

    # 使用PaddleOCR识别
    result = ocr_recognition(preprocessed_image)
    return result


if __name__ == '__main__':
    image = r'C:\IT\AI\OCR\two_ocr\src\DeepSeekOCR\img\e1ec55f0215e273947bb5a588bf511af.jpg'
    image_id = './img_1.png'
    # image = 'img.png'
    # 使用PaddleOCR识别
    # result = paddle_ocr(image_id)
    paddle_ocr(image, preprocessed_image_save_path=r"C:\IT\AI\OCR\two_ocr\src\PaddleOCR\pro\1.png")


    # 输出OCR结果
    # 确保输出文件夹存在
    # output_folder = "output"
    # os.makedirs(output_folder, exist_ok=True)
    #
    # # 输出结果文件完整路径
    # output_file_path = os.path.join(output_folder, "easyocr_results.txt")
    #
    # # 输出OCR结果到文件
    # with open(output_file_path, 'w', encoding='utf-8') as output_file:
    #     for detection in ocr_result:
    #         # 识别文本
    #         text = detection[1]
    #         # 向文件写入识别文本
    #         output_file.write(f"识别文本： {text}\n")
    #         # 如果需要，可以同时打印在控制台
    #         print(f"识别文本： {text}")

    # 显示处理过程中的每个阶段的图片
    # show_images(original_image, preprocessed_image)
