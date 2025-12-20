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
                                      use_safetensors=True,
                                      )
    model = model.eval().cuda().to(torch.bfloat16)

    # prompt = "<image>\nFree OCR. " 输出了带有检测框信息的markdown格式结果
    # prompts = "<image>\n<|grounding|>Convert the document to markdown. "

    # 输出只有结果的格式
    # prompts = "<image>\n<|grounding|>Convert the document to markdown.Extract the code text only."

    # 选项2 强调整体检测
    # prompts = "<image>\n<|grounding|>Convert the document to markdown and Extract the complete code block as one unified text region and Return a single bounding box covering all the code."
    prompts = "<image>\n<|grounding|>Extract the code text from the image."
    # prompt_text = "<image>\n<|grounding|>Convert the document to markdown and Transcribe the code verbatim according to the Markdown format and disabling autocomplete and Do NOT correct."
    # 2. 组装最终 Prompt (移除 <|grounding|>)
    # prompts = f"<image>\n<|grounding|>User: {prompts}\n\nAssistant:"

    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y405\test1\IMG_20250928_220327.jpg'
    image_file = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    # image_file = r'./8f79568af86c7fc3ff903f25fccde4ef.jpg' #漏检
    # image_file = r'./92e918d2af7ec92779a03c2c1b105465.jpg'
    # image_file = r'./68749e9f7995681ba856a5abfb447ec8.jpg'  # 中间会有坐标信息

    # image_file = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\20251029092659_105_33.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\uploads\processed_image\20251029092628_103_33.jpg' #输出全在一行：<table><tr><td>面向过程</td></tr><tr><td># include

    # image_file = r'./20251201220009_504_33.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y405\test2\IMG_20250928_220305.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y405\test1\IMG_20250928_220327.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y414\test1\a30463f8f8d2b2a4546a9b8f244c4361.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y418\test1\2531581a9f0d700aed369b710cdba02c.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\241042Y432\test1\26e0bb2f7f3221d092643d25f9cbd051.jpg'
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\2410450118\test1\IMG_20250928_220200.jpg'# 最后输出带着很多}

    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\2410450131\test1\IMG_20250928_220237.jpg'  # 识别乱码，代码写在左右，而且很多
    # image_file = r'C:\IT\AI\OCR\two_ocr\src\PaddleOCR\pro\1.png'  # 识别乱码的预处理图片
    # image_file = r'C:\IT\AI\OCR\two_ocr\Data\2410450238\test1\IMG_20250928_213227.jpg'  # 识别乱码，代码写在左右，而且很多

    # image_file = r'C:\IT\AI\OCR\two_ocr\src\DeepSeekOCR\cdb0fbcb986a47f7bf4302b51437f887.jpg'# 多图拼接
    # image_file = r'C:\IT\AI\OCR\two_ocr\uploads\original_image\57_b0d7a28b9198f71ca5a946d337748e24.jpg' # 内容很少，但是输出都在一行
    image_file = r'C:\IT\AI\OCR\two_ocr\src\DeepSeekOCR\20251211195955_39_62.jpg'# 1/5图

    image_file = r'C:\Users\UserY\OneDrive\图片\data\e1ec55f0215e273947bb5a588bf511af.jpg'



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
                      # save_results=False,
                      # eval_mode=True,
                      # output_path=None,  # 不设置输出路径
                      # save_results=False,  # 不保存结果 ， 可获取返回值
                      base_size=1280,
                      image_size=1280,
                      crop_mode=False,
                      test_compress=True,
                      )

    final = time.time() - since
    print("最终时间: ", final)
    # 添加这些代码来查看具体输出
    print("返回结果类型:", type(res))
    print("返回结果内容:")
    # 匹配并移除第一行的特殊标记
    # clean_text = re.sub(r'^<\|ref\|>.*?<\|/det\|>\s*\n?', '', res, flags=re.MULTILINE)
    # print(clean_text)
    clean_text = '\n'.join(line for line in re.sub(r'<\|ref\|>.*?<\|/det\|>', '', res).splitlines() if line.strip())

    print(clean_text)


if __name__ == '__main__':
    deepseek_ocr()
