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
    # since = time.time()
    model, tokenizer = global_models.get_ocr_model()

    # prompt = "<image>\nFree OCR. "
    # 输出了带有检测框信息的markdown格式结果
    # prompt = "<image>\n<|grounding|>Convert the document to markdown. "

    # 输出只有结果的格式
    prompts = "<image>\n<|grounding|>Convert the document to markdown.Extract the code text only."
    # prompts = "<image>\n<|grounding|>OCR the text exactly as it appears. Preserve all characters, spacing, and formatting without making any changes."
    # prompts = "<image>\n<|grounding|>识别图片中的内容"

    res = model.infer(tokenizer,
                      prompt=prompts,
                      image_file=image_file,
                      output_path=output_path,
                      save_results=False,
                      eval_mode=True,  # eval_mode 的默认值为 false，因此无法获得任何结果。
                      # output_path=None,  # 不设置输出路径
                      # save_results=False,  # 不保存结果 ， 可获取返回值
                      base_size=1024,
                      image_size=640,
                      crop_mode=True,
                      test_compress=True
                      )
    # final = time.time() - since
    # print("最终时间: ", final)
    # 匹配并移除第一行的特殊标记
    cleaned_res = re.sub(r'^<\|ref\|>.*?<\|/det\|>\s*\n?', '', res, flags=re.MULTILINE)
    # print(cleaned_res)
    return cleaned_res

if __name__ == '__main__':
    # image_file = '../../Data/241042Y414/test1/a30463f8f8d2b2a4546a9b8f244c4361.jpg'
    # image_file = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    image_file = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\test.jpg'
    output_path = './output'

    res = deepseek_ocr(image_file, output_path)
