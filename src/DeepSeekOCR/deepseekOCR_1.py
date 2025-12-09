import time

from transformers import AutoModel, AutoTokenizer
import torch
import os
import sys
from io import StringIO
# 从输出中提取OCR结果
import re
from core.core_llm.init_deepseek_ocr import global_models


# 捕获标准输出
# old_stdout = sys.stdout
# sys.stdout = captured_output = StringIO()


def deepseek_ocr(image_file, output_path):
    model, tokenizer = global_models.get_ocr_model()


    # 输出只有结果的格式
    # prompts = "<image>\n<|grounding|>Convert the document to markdown.Extract the code text only."
    prompts = "<image>\n<|grounding|>Convert the document to markdown and Extract the complete code block as one unified text region and Return a single bounding box covering all the code. "

    """
        Gundam:动态调整模型大小，当运行程序的时候，程序占用内存过大，模型动态调整大小，调成小模型，效果不会
    """
    res = model.infer(tokenizer,
                      prompt=prompts,
                      image_file=image_file,
                      output_path=output_path,
                      save_results=False,
                      eval_mode=True,  # eval_mode 的默认值为 false，因此无法获得任何结果。
                      # output_path=None,  # 不设置输出路径
                      # save_results=False,  # 不保存结果 ， 可获取返回值
                      base_size=1280,
                      image_size=1280,
                      crop_mode=False,
                      test_compress=False
                      )

    # 匹配并移除第一每一行的特殊标记
    cleaned_res = re.sub(r'^<\|ref\|>.*?<\|/det\|>\s*\n?', '', res, flags=re.MULTILINE)
    return cleaned_res

if __name__ == '__main__':
    image_file = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\test.jpg'
    output_path = './output'

    res = deepseek_ocr(image_file, output_path)
