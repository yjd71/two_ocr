import os
import shutil
import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

# ================= 配置区域 =================
# 替换为你的图片路径
IMAGE_PATH = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\IMG_20250928_220327.jpg'
# 模型路径
MODEL_PATH = 'C:/IT/AI/OCR/huggingface_deepseek_ocr_model/DeepSeek-OCR'
# 临时文件夹 (用于存放切分后的图片，避免模型读取报错)
TEMP_DIR = './temp_slices'


# ===========================================

def load_model():
    """加载 4-bit 量化模型以适配显存"""
    print("[1/4] 正在加载模型 (4-bit Config)...")

    # 1. 配置 4-bit 量化 (解决 Deprecation Warning)

    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        # 2. 加载模型
        model = AutoModel.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            device_map="auto",  # 自动分配 GPU
        )
        return tokenizer, model
    except Exception as e:
        print(f"FATAL ERROR: 模型加载失败: {e}")
        print("建议: 请确保安装了 Windows 版 bitsandbytes 并且 CUDA 环境配置正确。")
        exit()


def smart_split_image(image_path):
    """
    智能分栏：检测中间空白，物理切割图片。
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化反转 + 垂直投影
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    projection = np.sum(thresh, axis=0)

    # 寻找分割线
    center_start = int(w * 0.3)
    center_end = int(w * 0.7)
    mid_area = projection[center_start:center_end]
    min_val_index = np.argmin(mid_area) + center_start
    min_val = projection[min_val_index]

    # 判断是否双栏
    is_two_column = min_val < (255 * h * 0.02)

    if is_two_column:
        print(f"[2/4] 检测到双栏布局 (分割线 x={min_val_index})，正在物理切割...")
        left_img = img[:, :min_val_index]
        right_img = img[:, min_val_index:]
        left_pil = Image.fromarray(cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB))
        right_pil = Image.fromarray(cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB))
        return [left_pil, right_pil]
    else:
        print("[2/4] 检测为单栏布局，无需切割。")
        full_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 【关键修复】必须返回列表，防止 TypeError: 'NoneType' is not iterable
        return [full_pil]


def run_inference(tokenizer, model, image_path_str, part_idx):
    """
    执行推理
    注意：image_path_str 必须是硬盘上的文件路径，不能是 PIL 对象
    """
    print(f"[3/4] 正在识别第 {part_idx + 1} 部分...")

    # 【关键修复】优化 Prompt：
    # 1. 移除 <|grounding|> (防止空输出)
    # 2. 使用 User/Assistant 对话格式
    # 3. 使用英文指令 (模型理解力更好)
    prompt_content = (
        "Task: Transcribe the handwritten C++ code into a Markdown code block.\n"
        "Requirements:\n"
        "1. Strictly preserve the original formatting (indentation, line breaks).\n"
        "2. Do NOT auto-complete or fix errors. Transcribe verbatim.\n"
        "3. Ignore scribbles or crossed-out text.\n"
        "4. Output ONLY the code content."
    )

    # 构造对话模板
    prompt = f"<image>\nUser: {prompt_content}\n\nAssistant:"

    with torch.no_grad():
        # 注意：这里注释掉了不支持的 temperature 等参数，防止报错
        # 依赖模型默认的 greedy search (temperature=0) 逻辑
        result = model.infer(
            tokenizer,
            prompt=prompt,
            image_file=image_path_str,  # 传入路径字符串
            save_results=False,
            base_size=1024,
            image_size=640,
            crop_mode=True
        )

    # 简单的后处理：如果结果是字典，取 text；如果是字符串，直接用
    if isinstance(result, dict) and 'text' in result:
        return result['text']
    return str(result)


def main():
    # 0. 准备环境
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    # 1. 加载模型
    tokenizer, model = load_model()

    # 2. 预处理：智能切分图片
    try:
        pil_images = smart_split_image(IMAGE_PATH)
    except Exception as e:
        print(f"图片处理错误: {e}")
        return

    final_output = ""

    # 3. 依次识别每一部分
    for i, pil_img in enumerate(pil_images):
        # 【关键修复】将内存图片保存为临时文件
        # 因为 model.infer 无法直接处理 PIL 对象，只能读取路径
        temp_img_path = os.path.join(TEMP_DIR, f"part_{i}.jpg")
        pil_img.save(temp_img_path)

        try:
            # 传入临时文件路径
            text = run_inference(tokenizer, model, temp_img_path, i)

            # 清洗 Markdown 标记，方便最后拼接
            clean_text = text.replace("```cpp", "").replace("```", "").strip()
            final_output += clean_text + "\n\n"
        except Exception as e:
            print(f"推理阶段出错 (Part {i}): {e}")
        finally:
            # 可选：删除临时文件
            pass

            # 4. 最终输出
    print("\n" + "=" * 20 + " 最终识别结果 " + "=" * 20)
    print("```cpp")
    print(final_output.strip())
    print("```")
    print("=" * 50)

    # 清理临时目录
    # shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
    main()