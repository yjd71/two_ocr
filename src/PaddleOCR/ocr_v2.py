from  src.PaddleOCR.PaddleOCR import paddle_ocr

import re
import difflib


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


# 关键字列表（用于模糊匹配）
CPP_KEYWORDS = [
    "auto", "bool", "break", "case", "char", "class", "const", "continue", "default", "delete", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "namespace", "new",
    "private", "protected", "public", "return", "short", "signed", "sizeof", "static", "struct", "switch",
    "template", "this", "throw", "try", "typedef", "typename", "union", "unsigned", "using", "virtual", "void",
    "volatile", "while", "true", "false", "nullptr", "include", "using", "std", "cout", "cin", "endl", "exit",
    "push", "pop", "Stack", "buffer", "top", "STACK_SIZE"
]


# 基础规范化：全角->半角、中文标点->英文标点、压缩多余空白（保留换行与缩进）
def _normalize_fullwidth_and_punct(s: str) -> str:
    """基础规范化：全角->半角、中文标点->英文标点、压缩多余空白（保留换行与缩进）"""

    def fullwidth_to_ascii(ch):
        code = ord(ch)
        if code == 0x3000:
            return " "
        if 0xFF01 <= code <= 0xFF5E:
            return chr(code - 0xFEE0)
        return ch

    s = "".join(fullwidth_to_ascii(c) for c in s)
    replacements = {
        "，": ",", "。": ".", "：": ":", "；": ";", "（": "(", "）": ")",
        "【": "[", "】": "]", "“": '"', "”": '"', "‘": "'", "’": "'",
        "—": "-", "、": ",", "《": "<", "》": ">"
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    # 压缩非法空白（保留 \n）
    s = re.sub(r'[ \t\f\v]+', ' ', s)
    # 去掉行尾多余空格，但保留缩进
    s = "\n".join(line.rstrip() for line in s.splitlines())
    return s


# 模糊替换短 token 为常见关键字以修正 OCR 造成的错拼（保守）
def _keyword_fuzzy_fix(code: str, cutoff: float = 0.85, verbose=False):
    """模糊替换短 token 为常见关键字以修正 OCR 造成的错拼（保守）"""

    def replace_token(m):
        token = m.group(0)
        if token in CPP_KEYWORDS:
            return token
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]{0,11}$', token):
            return token
        cand = difflib.get_close_matches(token, CPP_KEYWORDS, n=1, cutoff=cutoff)
        if cand:
            if verbose:
                print(f"[kw-fix] {token} -> {cand[0]}")
            return cand[0]
        return token

    return re.sub(r'\b[A-Za-z_][A-Za-z0-9_]{0,11}\b', replace_token, code)


# 后处理 OCR 识别出来的代码字符串，返回修正后的代码字符串。（启发式规则）
def postprocess_code(code_str: str, verbose: bool = False) -> str:
    """
    进阶后处理 OCR 识别出的代码文本（启发式规则）。
    - 输入: code_str（原始或第一次后处理后的字符串）
    - 返回: 修正后的代码字符串
    说明: 规则尽量保守，同时包含一些针对 Stack push/pop 的启发式修复。
    """
    if not code_str:
        return ""

    code = _normalize_fullwidth_and_punct(code_str)

    # 1) 删除显然不是代码的行（仅含单个非 ASCII 字符、孤立标点或中文）
    cleaned_lines = []
    for ln in code.splitlines():
        s = ln.strip()
        if s.lower() == "date":
            if verbose: print("[drop] 'Date'")
            continue
        # 如果行包含 CJK（中文/日文/韩文）字符并且没有英文字母或数字，很可能是噪声，丢弃
        if re.search(r'[\u4e00-\u9fff]', s) and not re.search(r'[A-Za-z0-9_]', s):
            if verbose:
                print(f"[drop noisy line] {s!r}")
            continue
        # 丢弃非常短、且仅由单字符或孤立符号构成的行
        if len(s) <= 1 and not re.search(r'[A-Za-z0-9]', s):
            if verbose:
                print(f"[drop short non-code] {s!r}")
            continue
        cleaned_lines.append(ln)
    code = "\n".join(cleaned_lines)

    # 2) 修正双重 <<（例如: '<< <<' 或 '<< << "...'）
    code, n = re.subn(r'<<\s*<<', '<<', code)
    if verbose and n:
        print(f"[fix <<<<] replaced {n} occurrences of '<< <<'")

    # 3) 修正 cout 的典型误识别：coutc" -> cout << "
    code = re.sub(r'\bcout\s*[cC]\s*["\']', 'cout << "', code)
    code = re.sub(r'\bcoutic\b', 'cout <<', code)
    code = re.sub(r'\bcoutc\b', 'cout <<', code)
    # 修正一些 'cout << <<"...' 导致的重复 << 后边紧跟引号的情况
    code = re.sub(r'<<\s*<<\s*"', '<< "', code)
    code = re.sub(r'<<\s*<<\s*\'', '<< \'', code)

    # 4) 在字符串内把常见的 `.n`、`/n`、` \ n` 等修为真正的转义 \\n （在源代码文件中希望看到的是 \\n）
    def _fix_newline_in_strings(s):
        # 把 ".n" 或 ".\n-like" 转为 "\\n"（保留引号）
        s = re.sub(r'(?<=["\'])\s*\.n(?=["\'])', r'\\n', s)  # "overflow.n" -> "overflow\n"
        s = re.sub(r'(?<=["\'])\\\s?n(?=["\'])', r'\\n', s)
        # 有时写成 "empty,n" -> "empty\n"
        s = re.sub(r'(?<=["\'])\s*,\s*n(?=["\'])', r'\\n', s)
        return s

    # 对整段文本中的引号内内容进行替换（更稳妥）
    def replace_in_quotes(match):
        inner = match.group(1)
        inner_fixed = _fix_newline_in_strings('"' + inner + '"')[1:-1]
        return '"' + inner_fixed + '"'

    code = re.sub(r'"([^"]*)"', replace_in_quotes, code)

    # 5) 修正 STACK_SZZE -> STACK_SIZE（以及类似明显字母错位）
    code = re.sub(r'STACK[_\s]*S?Z+E', 'STACK_SIZE', code, flags=re.IGNORECASE)

    # 6) 修正 push / pop 函数名常见 OCR 错误（保守做法）
    # pushcinti -> push(int i)
    code = re.sub(r'\bpush\w*int\w*\b', 'push(int i)', code, flags=re.IGNORECASE)
    # 修正类似 "void Stack :poPCint &i)" -> "void Stack::pop(int &i)"
    code = re.sub(r'void\s+Stack\s*[:]\s*poP?C?int\s*&\s*i\)', 'void Stack::pop(int &i)', code, flags=re.IGNORECASE)
    # 如果出现 "Stack :poPCint" 也修
    code = re.sub(r'Stack\s*[:]\s*poP?C?int', 'Stack::pop', code, flags=re.IGNORECASE)

    # 更通用：把 ":\s*poP.*int" -> "::pop(int"
    code = re.sub(r':\s*poP\w*\s*int', '::pop(int', code, flags=re.IGNORECASE)

    # 7) 针对 push 的内部语句修复 buffer[++top] 模式
    # 如果行像 '_{toptt;buffer[top]}=i;' 或包含 'buff...top' 且在 push 函数上下文，则修为 'buffer[++top] = i;'
    code = re.sub(r'_\{top\w*;buffer\[top\]\}\s*=\s*i\s*;', 'buffer[++top] = i;', code)
    code = re.sub(r'buffer\[top\]', 'buffer[++top]', code)  # 先保守替换（后面若出现 pop 再调整）
    # 但如果紧接着是 pop 块（i = buffer[...]），下面会被覆盖

    # 8) 针对 pop 的内部语句修复 'i=buffer[top]]; top-' -> 'i = buffer[top--];'
    code = re.sub(r'i\s*=\s*buffer\[top\]\]\s*;\s*top-', 'i = buffer[top--];', code)
    # 若出现 'top-' 单独一行或尾部，尽可能修为 'top--;' 或合并到上行变为 'buffer[top--]'
    code = re.sub(r'\btop-\b', 'top--', code)
    # 把 'buffer[top]]' -> 'buffer[top]'（多余括号）
    code = re.sub(r'buffer\[top\]\]', 'buffer[top]', code)

    # 如果看到 'i = buffer[top]; top--' 两行，将合并为 'i = buffer[top--];'
    code = re.sub(r'i\s*=\s*buffer\[top\]\s*;\s*\n\s*top--\s*;', 'i = buffer[top--];', code,
                  flags=re.IGNORECASE | re.MULTILINE)

    # 9) 修正 return 拼写（保守）
    code = _keyword_fuzzy_fix(code, cutoff=0.80, verbose=verbose)

    # 10) 删除或修正显然的孤立垃圾行（like single '[' or stray 'a'）
    lines = []
    for ln in code.splitlines():
        s = ln.strip()
        # 删除仅为单个 '[' 或 ']' 或单字母 'a' 且无其它字母数字的行
        if re.fullmatch(r'[\[\]\{\}]', s):
            if verbose:
                print(f"[drop bracket line] {s}")
            continue
        if re.fullmatch(r'[aAiI]', s):
            if verbose:
                print(f"[drop single-letter line] {s}")
            continue
        # 删除包含非 ASCII 且没有字母数字的行（噪声）
        if re.search(r'[\u4e00-\u9fff]', s) and not re.search(r'[A-Za-z0-9_]', s):
            continue
        lines.append(ln)
    code = "\n".join(lines)

    # 11) 再次确保常见语句结尾有分号（保守）
    new_lines = []
    for ln in code.splitlines():
        s = ln.rstrip()
        s_stripped = s.strip()
        if not s_stripped:
            new_lines.append(s)
            continue
        # 对包含 cout/return/exit/printf/puts/scanf/assign-buffer 的行加分号（如果缺失）
        if (re.search(r'\bcout\b', s) or re.search(r'\breturn\b', s) or re.search(r'\bexit\s*\(', s)
                or re.search(r'=\s*buffer\[', s)):
            if not re.search(r'[;{}\:]$', s):
                s = s + ";"
                if verbose:
                    print(f"[add ;] {s}")
        new_lines.append(s)
    code = "\n".join(new_lines)

    # 12) 最后做一点清理：去掉多余空行（最多保留两个连续空行）
    code = re.sub(r'\n{3,}', '\n\n', code)

    return code


if __name__ == '__main__':
    image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
    # 使用PaddleOCR识别 的结果，
    results = paddle_ocr(image)
    # #  保存识别结果的图片和json数据
    # for res in results:
    #     # res.print()
    #     # print(res["rec_texts"])
    #     res.save_to_img("output")
    #     res.save_to_json("output")

    # 把 OCR 的 rec_texts（字符串列表）拼成一个包含换行符的源代码字符串。在内存中执行 OCR 并直接返回拼接好的源代码字符串（不写文件）。
    code_str = ocr_recognition_return_string(results)

    # 合并为 string（和之前给的合并函数等价）
    print("=== 原始 OCR 字符串 ===")
    print(code_str)

    # 后处理 OCR 识别出来的代码字符串，返回修正后的代码字符串。
    corrected = postprocess_code(code_str, verbose=True)
    print("\n=== 后处理后 ===")
    print(corrected)
