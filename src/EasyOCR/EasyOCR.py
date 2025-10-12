import os

import cv2
import numpy as np
import matplotlib
# 使用 PyQt5 后端来支持交互式绘图
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import easyocr

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置 Matplotlib 字体为黑体，支持中文显示
plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负号显示为方块的问题


# 加载图片
def load_img(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Image not loaded correctly")
    return img


# 图片预处理
def preprocess_img_pro(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转化为灰度图
    blurred = cv2.GaussianBlur(gray_image, (7, 7), 0)  # 对灰度图进行高斯模糊，去除图片中的噪声

    # 轻度高斯平滑，降噪减弱孤立噪点
    H, W = image.shape[:2]
    base = max(1, int(round(min(H, W) / 256.0)))  # 自适应尺度
    g = cv2.GaussianBlur(blurred, (2 * base + 1, 2 * base + 1), 0)

    # 自适应阈值处理以改善文字识别
    binary_img = cv2.adaptiveThreshold(g, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
    # _, binary_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU,)  # 二值化处理
    # 形态学操作：开运算去除噪声
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel)

    return opening


# 使用EasyOCR识别
def ocr_recognition(image):
    reader = easyocr.Reader(['en'], gpu=True,
                            model_storage_directory='../../easyocr/model')  # 初始化 ocr 引擎， 设置语言为英文和中文, model_storage_directory：自定义模型存储路径
    result = reader.readtext(image,  # image：支持文件路径、URL、字节数据或Opencv格式图像
                             detail=1,  # detail: 是否返回位置信息（默认1返回全部信息）
                             paragraph=False,  # paragraph:是否合并为段落(默认False）
                             contrast_ths=0.5,  # contrast_ths：对比度阈值(调整识别灵敏度）
                             adjust_contrast=1.2,  # adjust_contrast：自动调整输入图像的对比度，增强文字与背景的区分度
                             )
    return result


# 显示和保存每个阶段的图像
def show_images(original, opening):
    import cv2
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title('Original Image')
    axes[0].axis('off')

    axes[1].imshow(opening, cmap='gray')
    axes[1].set_title('Preprocessed Image')
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    # 加载图片
    original_image = load_img(image)
    # 图片预处理
    preprocessed_image = preprocess_img_pro(original_image)

    # 使用EasyOCR识别
    ocr_result = ocr_recognition(preprocessed_image)

    # 输出OCR结果
    # 确保输出文件夹存在
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # 输出结果文件完整路径
    output_file_path = os.path.join(output_folder, "easyocr_results.txt")

    # 输出OCR结果到文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for detection in ocr_result:
            # 识别文本
            text = detection[1]
            # 向文件写入识别文本
            output_file.write(f"识别文本： {text}\n")
            # 如果需要，可以同时打印在控制台
            print(f"识别文本： {text}")

    # 显示处理过程中的每个阶段的图片
    show_images(original_image, preprocessed_image)