import re
import time

from transformers import AutoModel, AutoTokenizer
import torch
import os





def deepseek_ocr():
    since = time.time()
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'

    model_name = 'C:/IT/AI/OCR/huggingface_deepseek_ocr_model/DeepSeek-OCR'

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name,
                                      trust_remote_code=True,
                                      use_safetensors=True)
    model = model.eval().cuda().to(torch.bfloat16)

    # prompt = "<image>\nFree OCR. " 输出了带有检测框信息的markdown格式结果
    # prompt = "<image>\n<|grounding|>Convert the document to markdown. "

    # 输出只有结果的格式
    prompts = "<image>\n<|grounding|>Convert the document to markdown.Fix format errors.Extract the code text only."
    # prompts = "<image>\n<|grounding|>OCR the text exactly as it appears. Preserve all characters, spacing, and formatting without making any changes."
    # prompts = "<image>\n<|grounding|>识别图片中的内容"



    # image_file = '../../Data/241042Y414/test1/a30463f8f8d2b2a4546a9b8f244c4361.jpg'
    # image_file = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    image_file = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\test.jpg'

    output_path = './output'

    # infer(self, tokenizer, prompt='', image_file='', output_path = ' ', base_size = 1024, image_size = 640, crop_mode = True, test_compress = False, save_results = False):

    # Tiny: base_size = 512, image_size = 512, crop_mode = False
    # Small: base_size = 640, image_size = 640, crop_mode = False
    # Base: base_size = 1024, image_size = 1024, crop_mode = False
    # Large: base_size = 1280, image_size = 1280, crop_mode = False

    # Gundam: base_size = 1024, image_size = 640, crop_mode = True
    res = model.infer(tokenizer,
                      prompt=prompts,
                      image_file=image_file,
                      output_path=output_path,
                      save_results=True,
                      # eval_mode=True,
                      # output_path=None,  # 不设置输出路径
                      # save_results=False,  # 不保存结果 ， 可获取返回值
                      base_size=1024,
                      image_size=640,
                      crop_mode=True,
                      test_compress=True
                      )

    final = time.time() - since
    print("最终时间: ", final)
    # # 添加这些代码来查看具体输出
    print("返回结果类型:", type(res))
    print("返回结果内容:")
    # 匹配并移除第一行的特殊标记
    cleaned_res = re.sub(r'^<\|ref\|>.*?<\|/det\|>\s*\n?', '', res, flags=re.MULTILINE)
    print(cleaned_res)




if __name__ == '__main__':
    deepseek_ocr()
