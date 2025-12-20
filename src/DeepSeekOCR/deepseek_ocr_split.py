import re
import time
from PIL import Image
from transformers import AutoModel, AutoTokenizer
import torch
import os

from src.DeepSeekOCR.utils.clean_hard_end_result import clean_ocr_edges_only
from src.DeepSeekOCR.utils.smart_merge import smart_merge
from src.DeepSeekOCR.utils.split_image_vertically import split_image_vertically


def deepseek_ocr_split(image_file, output_path):
    since = time.time()

    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    model_name = 'C:/IT/AI/OCR/huggingface_deepseek_ocr_model/DeepSeek-OCR'
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name,
                                      trust_remote_code=True,
                                      use_safetensors=True,
                                      )
    model = model.eval().cuda().to(torch.bfloat16)
    """接口调用注释以上代码，打开下面的调用全局的model和tokenizer"""
    # model, tokenizer = global_models.get_ocr_model()

    prompt_text = "<image>\n<|grounding|>Convert the document to markdown and Transcribe the code verbatim according to the Markdown format and disabling autocomplete and Do NOT correct"
    # 2. 组装最终 Prompt (移除 <|grounding|>)
    prompts = f"<image>\n<|grounding|>User: {prompt_text}\n\nAssistant:"

    temp_slice_dir = './temp_slices'  # 临时文件夹

    # ================= 核心切片逻辑 =================
    print(f"正在对图片进行切片处理: {image_file}")

    """
     根据图片长宽比或者固定逻辑决定切几份，这里num_slices=3：切成3份，overlap_ratio=0.1：两张图片之间重叠10%
     return: 切片文件路径列表: temp_slice_dir目录下
    """
    slice_paths = split_image_vertically(image_file, temp_slice_dir, num_slices=3, overlap_ratio=0.1)

    # 切片列表，在循环中合并切片的识别内容
    full_text_results = []

    print(f"图片已切分为 {len(slice_paths)} 份，开始逐一推理...")

    for idx, slice_path in enumerate(slice_paths):
        print(f"正在处理切片 {idx + 1}/{len(slice_paths)}: {slice_path}")
        current_base_size = 1280

        res = model.infer(tokenizer,
                          prompt=prompts,
                          image_file=slice_path,
                          output_path=output_path,
                          # save_results=True,
                          save_results=False,
                          eval_mode=True,
                          base_size=current_base_size,
                          image_size=current_base_size,
                          crop_mode=False,  # 切片后通常不需要模型内部再 crop
                          test_compress=True,  # 开启压缩可能影响速度
                          )

        # 清理单个切片的输出
        clean_text = '\n'.join(line for line in re.sub(r'<\|ref\|>.*?<\|/det\|>', '', res).splitlines() if line.strip())
        full_text_results.append(clean_text)
        print("-" * 60)
        print("切片", idx, "识别结果：")
        print(clean_text)

    # ================= 结果合并 (使用智能去重) =================
    print("-" * 60)
    print("正在智能合并切片结果...")

    """
     调用 smart_merge，传入拼接合并的 full_text_results 整个列表,
     full_text_results[0],[1],[2]：各个分片的识别结果, 智能合并有重叠的代码片段，去掉重复的代码
    """
    final_code = smart_merge(
        full_text_results,
        search_window=10,  # 针对重叠，10行足够覆盖
        threshold=0.8  # 稍微宽松一点的阈值
    )

    print("-" * 60)
    final = time.time() - since
    print(f"最终总耗时: {final:.2f}s")

    print("-" * 60)
    print("最终识别结果 final_code :")
    print(final_code)
    print("-" * 60)
    print("清理非法开头和结尾后的 final_code :")
    final_code = clean_ocr_edges_only(final_code)
    print(final_code)

    # 清理临时文件
    # shutil.rmtree(temp_slice_dir)

    return final_code


if __name__ == '__main__':
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\2410450118\test1\IMG_20250928_220200.jpg'
    image_file = r'C:\Users\UserY\OneDrive\图片\data\e1ec55f0215e273947bb5a588bf511af.jpg'

    output_path = './output'

    final_code = deepseek_ocr_split(image_file, output_path)
