import logging

import cv2
import numpy as np
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


# 加载图片
def load_img(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Image not loaded correctly")
    return img


# 图片预处理
def preprocess_img_pro(image):
    # 转化为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 对灰度图进行高斯模糊，去除图片中的噪声
    blurred = cv2.GaussianBlur(gray_image, (7, 7), 0)

    # 轻度高斯平滑，降噪减弱孤立噪点
    H, W = image.shape[:2]
    base = max(1, int(round(min(H, W) / 256.0)))  # 自适应尺度
    g = cv2.GaussianBlur(blurred, (2 * base + 1, 2 * base + 1), 0)

    # 自适应阈值处理以改善文字识别（二值化）
    binary_img = cv2.adaptiveThreshold(g, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
    # _, binary_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU,)  # 二值化处理
    # 形态学操作：开运算去除噪声
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel)
    # back to BGR uint8
    preprocessed = cv2.cvtColor(opening, cv2.COLOR_GRAY2BGR)

    return preprocessed


# 使用PaddleOCR识别
def ocr_recognition(image):
    # 初始化 ocr 引擎
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_server_det",
        text_recognition_model_name="PP-OCRv5_server_rec",
        use_doc_orientation_classify=True,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
        use_doc_unwarping=True,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
        use_textline_orientation=True,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
        lang="en",  # 通过 lang 参数来使用英文模型
        # device="gpu",  # 通过 device 参数使得在模型推理时使用 GPU
        # text_detection_model_dir="../../paddleocr/_pipelines"# 通过 text_detection_model_dir 指定本地模型路径
        # ocr_version="PP-OCRv4" # 通过 ocr_version 参数来使用 PP-OCR 其他版本
    )

    result = ocr.predict(image)

    """
       保存识别结果的图片和json数据
    """
    # for res in result:
    #     # res.print()
    #     # print(res["rec_texts"])
    #     res.save_to_img("output")
    #     res.save_to_json("output")

    return result


# ocr调用函数
def paddle_ocr(image):
    # 加载图片
    original_image = load_img(image)
    # 图片预处理
    preprocessed_image = preprocess_img_pro(original_image)

    # 使用PaddleOCR识别
    result = ocr_recognition(preprocessed_image)
    return result


if __name__ == '__main__':
    image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'

    # 使用PaddleOCR识别
    result = paddle_ocr(image)

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
