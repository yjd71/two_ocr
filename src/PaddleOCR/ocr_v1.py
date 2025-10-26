from PaddleOCR import paddle_ocr


# 把 OCR 的 rec_texts（字符串列表）拼成一个包含换行符的源代码字符串。
def rec_texts_list_to_code_string(rec_texts):
    """
    把 OCR 的 rec_texts（字符串列表）拼成一个包含换行符的源代码字符串。
    输入:
        rec_texts: list[str] 或 单个 str（或 None）
    返回:
        code_str: str （以换行符连接，每行末尾加一个换行）
    """
    if rec_texts is None:
        return ""
    if isinstance(rec_texts, str):
        return rec_texts if rec_texts.endswith("\n") else rec_texts + "\n"

    # 过滤 None 和只含空白的条目，去掉首尾空白
    lines = [s.strip() for s in rec_texts if isinstance(s, str) and s.strip() != ""]
    if not lines:
        return ""
    # 将每个识别出的“行”用换行符连接，最后加一个换行符
    code_str = "\n".join(lines) + "\n"
    return code_str


# 在内存中执行 OCR 并直接返回拼接好的源代码字符串（不写文件）。
def ocr_recognition_return_string(results):
    collected = []

    for res in results:
        # res.print()
        # print(res["rec_texts"])
        res.save_to_img("output")
        res.save_to_json("output")

    # 递归查找并提取所有可能的文本行（兼容 dict/list/object 等结构）
    def find_and_collect(obj):
        if obj is None:
            return
        # 普通 dict，寻找键 'rec_texts' 或 'text' 等
        if isinstance(obj, dict):
            # 直接有 rec_texts 字段（你的场景）
            if "rec_texts" in obj and isinstance(obj["rec_texts"], list):
                for s in obj["rec_texts"]:
                    if isinstance(s, str):
                        collected.append(s)
                return
            # 有可能是每个条目是 {'text': '...', ...}
            if "text" in obj and isinstance(obj["text"], str):
                collected.append(obj["text"])
                return
            # 否则遍历所有 value
            for v in obj.values():
                find_and_collect(v)
            return

        # 列表或元组：常见 paddle 返回格式
        if isinstance(obj, (list, tuple)):
            # 常见单条结构： [bbox, (text, score)] 或 [bbox, text] 或 [ [x1,y1], ... , ['text', conf] ]
            # 遍历元素并尝试解析
            # 尝试常见 pattern：第二项为 (text, score) 或 [text, score]
            if len(obj) >= 2:
                second = obj[1]
                # case: (text, score)
                if isinstance(second, (list, tuple)) and len(second) >= 1 and isinstance(second[0], str):
                    collected.append(second[0])
                    # 继续遍历以防 nested
                    for it in obj:
                        find_and_collect(it)
                    return
                # case: second directly is a str
                if isinstance(second, str):
                    collected.append(second)
                    for it in obj:
                        find_and_collect(it)
                    return
            # 如果不是上述简单结构，就逐项递归查找
            for it in obj:
                find_and_collect(it)
            return

        # 对象（可能有属性 rec_texts）
        # 例如某些版本返回的对象有 .rec_texts 属性
        try:
            rec_attr = getattr(obj, "rec_texts", None)
            if isinstance(rec_attr, list):
                for s in rec_attr:
                    if isinstance(s, str):
                        collected.append(s)
                return
        except Exception:
            pass

        # 不能解析的类型，忽略
        return

    # 提取文本
    find_and_collect(results)

    # 拼成最终代码字符串
    code_str = rec_texts_list_to_code_string(collected)
    return code_str


def ocr_v1():
    image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    # 使用PaddleOCR识别 的结果
    results = paddle_ocr(image)
    code_str = ocr_recognition_return_string(results)
    print(code_str)


if __name__ == '__main__':
    ocr_v1()
