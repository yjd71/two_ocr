import re
import difflib

# 关键字列表（用于模糊匹配修正）
CPP_KEYWORDS = [
    "auto","bool","break","case","char","class","const","continue","default","delete","do","double",
    "else","enum","extern","float","for","goto","if","inline","int","long","namespace","new",
    "private","protected","public","return","short","signed","sizeof","static","struct","switch",
    "template","this","throw","try","typedef","typename","union","unsigned","using","virtual","void",
    "volatile","while","true","false","nullptr","include","using","std","cout","cin","endl","exit"
]

def _normalize_fullwidth_and_punct(s: str) -> str:
    """把常见全角字符、中文标点转换为半角/ASCII 标点，并修正常见全角数字字母。"""
    # 全角->半角转换 (简单实现)
    def fullwidth_to_ascii(ch):
        code = ord(ch)
        # 全角空格
        if code == 0x3000:
            return " "
        # 全角字符范围
        if 0xFF01 <= code <= 0xFF5E:
            return chr(code - 0xFEE0)
        return ch

    s = "".join(fullwidth_to_ascii(c) for c in s)

    # 中文标点替换
    replacements = {
        "，": ",", "。": ".", "：": ":", "；": ";", "（": "(", "）": ")",
        "【": "[", "】": "]", "“": '"', "”": '"', "‘": "'", "’": "'",
        "—": "-", "、": ",", "《": "<", "》": ">"
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # 去除奇怪的控制字符但保留常用空白和换行
    s = re.sub(r"[^\S\r\n]+", " ", s)  # 把各种空白压缩成单个空格（保留换行）
    return s

def _keyword_fuzzy_fix(code: str, cutoff: float = 0.85, verbose=False):
    """
    对较短的单词做模糊匹配关键字修正。
    仅处理长度<=12 且含字母的 token（避免把长标识符错改掉）。
    """
    def replace_token(m):
        token = m.group(0)
        # 如果已经是正确关键字，不动
        if token in CPP_KEYWORDS:
            return token
        # 只对纯字母/下划线开头的 token 处理
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]{0,11}$', token):
            return token
        # 模糊匹配
        cand = difflib.get_close_matches(token, CPP_KEYWORDS, n=1, cutoff=cutoff)
        if cand:
            if verbose:
                print(f"Keyword fix: '{token}' -> '{cand[0]}'")
            return cand[0]
        return token

    # 使用正则替换 token
    return re.sub(r'\b[A-Za-z_][A-Za-z0-9_]{0,11}\b', replace_token, code)

def postprocess_code(code_str: str, verbose: bool = False) -> str:
    """
    后处理 OCR 识别出来的代码字符串，返回修正后的代码字符串。
    参数:
        code_str: 原始 OCR 识别后的字符串（多行）
        verbose: 若 True 会在控制台打印主要替换动作的摘要
    返回:
        修正后的代码字符串
    """
    if not code_str:
        return ""

    orig = code_str

    # 1) 基础规范化：全角->半角，中文标点->英文标点，压缩空白
    code = _normalize_fullwidth_and_punct(code_str)
    if verbose and code != orig:
        print("[Normalize] applied fullwidth/punct normalization")

    # 2) 常见字符串内的 OCR 错误修正（如 overflow.n -> overflow.\n ）
    #    在双引号或单引号内把 `.n` 或 `.r.n` 之类修为 `\\n`
    def _fix_string_newline_literals(s):
        # 将 .n 或 \.n 等在字符串中转换为 \n
        s = re.sub(r'(\\?\.n)(?=["\'])', r'\\n', s)
        # 有时会把 \\n 识别为 \ n 或 /n，做额外修正
        s = re.sub(r'(\\\s?n)', r'\\n', s)
        return s

    # 对每行里在引号内的部分进行替换
    def _process_string_literals(line):
        # 处理双引号和单引号字符串
        def repl_double(m):
            inner = m.group(1)
            return '"' + _fix_string_newline_literals(inner) + '"'
        line = re.sub(r'"([^"]*)"', repl_double, line)
        def repl_single(m):
            inner = m.group(1)
            return "'" + _fix_string_newline_literals(inner) + "'"
        line = re.sub(r"'([^']*)'", repl_single, line)
        return line

    lines = code.splitlines()
    lines = [_process_string_literals(ln) for ln in lines]
    code = "\n".join(lines)

    # 3) 针对 cout/cin/cerr 的 OCR 特殊修复
    # 常见 OCR 将 '<<' 识别为 'c' 或 'c<' 等，或将 coutc"Stack -> cout << "Stack
    # 先把 `coutc"` / `coutc '` / `coutic` 等模式修为 'cout << "'
    cout_patterns = [
        (r'\bcout\s*[cC]\s*["\']', 'cout << "'),
        (r'\bcout\s*[cC]\s*\<\<', 'cout << <<'),  # unlikely but safe
        (r'\bcoutic\b', 'cout <<'),
        (r'\bcoutc\b', 'cout <<'),
        (r'\bcout\<\<\s*', 'cout << ')
    ]
    for pat, repl in cout_patterns:
        new_code = re.sub(pat, repl, code)
        if new_code != code and verbose:
            print(f"[cout fix] {pat} -> {repl}")
        code = new_code

    # 更通用地： 如果出现 cout 后接 非字母数字并包括 " 的情况，插入 '<<'
    code = re.sub(r'\bcout\s+(?=["<])', 'cout << ', code)

    # 4) 修正常见 buffer/top 之类的 OCR 导致拼写错误，尝试把 buff...top -> buffer[top]
    # 匹配类似 buff...top 的词，把它替换为 buffer[top]
    code = re.sub(r'\bbuf\w{0,8}top\w*\b', 'buffer[top]', code)
    if verbose:
        # 如果替换发生，告知
        if 'buffer[top]' in code:
            print("[buffer fix] replaced buf...top -> buffer[top]")

    # 5) 把一些明显的 OCR 错词（retunj, retun, reutrn, retunr 等）修为 return
    # 通过模糊关键字替换
    code = _keyword_fuzzy_fix(code, cutoff=0.82, verbose=verbose)

    # 6) 替换常见 punctuation 错误：把 'i' 尾部误识 '-' 或 '|' 的情形（举例）
    #    （此处仅做非常保守的替换）
    code = re.sub(r'exit\(\s*=\s*([0-9]+)\s*\)\s*i', r'exit(\1);', code)  # exit(=1)i -> exit(1);
    code = re.sub(r'exit（\s*-\s*1\)\s*i', 'exit(-1);', code)  # 全角符号的奇怪形式
    # 如果有出现 exit(1)i 或 exit(1)I 也修复
    code = re.sub(r'exit\(\s*([0-9\-]+)\s*\)\s*[iI]', r'exit(\1);', code)

    # 7) 补全常见语句尾的分号（启发式）
    new_lines = []
    for ln in code.splitlines():
        s = ln.rstrip()
        s_stripped = s.strip()
        if not s_stripped:
            new_lines.append(s)
            continue

        # 如果这一行包含 cout 或 return 或 exit( 并且不以 ; 结尾，则补 ;
        if (re.search(r'\bcout\b', s) or re.search(r'\breturn\b', s) or re.search(r'\bexit\s*\(', s)
                or re.search(r'\bprintf\b', s) or re.search(r'\bputs\b', s) or re.search(r'\bscanf\b', s)):
            # 如果已经以 ; 或 { 或 } 或 : 结尾，跳过
            if not re.search(r'[;{}\:]$', s):
                # 但若是以 ) 结尾，需要判断是否是函数/if/for/while 的头——我们只对包含 cout/return/exit/printf/puts/scanf 做补 ;，相对安全
                s = s + ";"
                if verbose:
                    print(f"[semicolon added] -> {s}")
        new_lines.append(s)
    code = "\n".join(new_lines)

    # 8) 修正由 OCR 导致的错误方括号/花括号顺序（非常保守）
    # 例如有的行出现 "top- " 等，尝试将 'top-' 修为 'top]' 可能风险大，暂保守不自动替换

    # 9) 额外：修正一些明显拼写 -> 标识符恢复，如 retunj -> return 已由模糊匹配完成

    # 10) 清理多余空格（保留缩进）
    def clean_trailing_ws(line):
        # 保留前导空格（缩进），去掉行尾多余空格
        m = re.match(r'^(\s*)(.*\S)?\s*$', line)
        if m:
            indent, body = m.group(1), (m.group(2) or "")
            return indent + body
        return line

    code_lines = [clean_trailing_ws(ln) for ln in code.splitlines()]
    code = "\n".join(code_lines)

    return code


# --------------------
# 示例：把你给的 sample rec_texts 拼成 code_str，然后后处理
if __name__ == "__main__":
    sample = [
        "Date",
        "void Stack::pushcinti",
        "{ifctep==STACK_SZZE-1)",
        "coutc\"Stack is overflow.n\"",
        "exit(=1)i",
        "else",
        "_{toptt;buffecitop}=i;",
        "a",
        "void Stack :poPCint &i)",
        "{coutic\"Stack is empty,n\";",
        "exit（-1)i",
        "else",
        "{i=buflerItop]; top-",
        "retunj",
        "[",
        "了"
    ]
    # 合并为 string（和我之前给你的合并函数等价）
    code_str = "\n".join(sample) + "\n"
    print("=== 原始 OCR 字符串 ===")
    print(code_str)

    corrected = postprocess_code(code_str, verbose=True)
    print("\n=== 后处理后 ===")
    print(corrected)
