import re


def clean_ocr_edges_only(text, head_lines=5, tail_lines=5):
    """
    只检查和清理开头和结尾的几行，保持中间内容不变
    1. [清洗开头] 移除页眉 (No., Date.)
    2. [清洗结尾] 移除页脚/页码 (301/代码, Page 1)
    3. [清洗边缘] 移除噪点
    4. [修复边缘] 为无注释的中文行添加 //

    参数:
        text: 待处理的文本
        head_lines: 检查开头的行数（默认5行）
        tail_lines: 检查结尾的行数（默认5行）
    """
    if not text:
        return ""

    lines = text.splitlines()
    if len(lines) == 0:
        return ""

    # === 正则定义 ===
    patterns = {
        # 页眉
        "header": re.compile(r'^(no\.|date[\.:]?|page|title|日期|时间|页码)\s*.*', re.IGNORECASE),
        # 页脚
        "footer": re.compile(r'^[\d\s/\-\.]+(\w+|[\u4e00-\u9fa5]+)?$', re.IGNORECASE),
        # 噪点
        "noise": re.compile(r'^[\.,_~\|\-\=]$'),
        # 中文开头
        "starts_with_chinese": re.compile(r'^[\u4e00-\u9fa5]')
    }

    def process_line(line, is_edge=True):
        """处理单行，is_edge表示是否是边缘行"""
        content = line.strip()

        # 保留空行
        if not content:
            return line, True

        # 如果不是边缘行，直接返回原行
        if not is_edge:
            return line, True

        # 白名单保护：已有注释符号的行
        if content.startswith("//") or content.startswith("/*") or content.startswith("#"):
            return line, True

        # 过滤页眉
        if patterns["header"].match(content):
            is_real_code = any(c in content for c in ['=', ';', '{', '('])
            if not is_real_code:
                return None, False

        # 过滤页脚
        if patterns["footer"].match(content):
            is_real_code = any(c in content for c in ['=', ';', '{', '(', 'return', 'int ', 'void '])
            if not is_real_code:
                return None, False

        # 过滤噪点
        if patterns["noise"].match(content):
            return None, False

        # 处理中文注释缺失
        if patterns["starts_with_chinese"].match(content):
            indent = line[:len(line) - len(line.lstrip())]
            line = f"{indent}// {content}"

        return line, True

    # 分离开头、中间、结尾
    total_lines = len(lines)

    # 如果总行数很少，全部作为边缘处理
    if total_lines <= head_lines + tail_lines:
        cleaned_lines = []
        for line in lines:
            processed_line, keep = process_line(line, is_edge=True)
            if keep and processed_line is not None:
                cleaned_lines.append(processed_line)
        return "\n".join(cleaned_lines)

    # 处理开头
    head_cleaned = []
    for i in range(head_lines):
        processed_line, keep = process_line(lines[i], is_edge=True)
        if keep and processed_line is not None:
            head_cleaned.append(processed_line)

    # 中间部分完全保留
    middle_lines = lines[head_lines:total_lines - tail_lines]

    # 处理结尾
    tail_cleaned = []
    for i in range(total_lines - tail_lines, total_lines):
        processed_line, keep = process_line(lines[i], is_edge=True)
        if keep and processed_line is not None:
            tail_cleaned.append(processed_line)

    # 合并结果
    result_lines = head_cleaned + middle_lines + tail_cleaned
    return "\n".join(result_lines)

if __name__ == '__main__':
    final_code = """No. 
    Date. 
    这是代码
    const int STACK_SIZE = 100; // 100
    int stack_top = -1;
    int stack_buffer[STACK_SIZE];
    void stack_init()
    {
        // 初始化
        stack_top = -1;
    }
    // 初始化栈
    bool stack_isEmpty() {
        return stack_top == -1;
    }
    // 判断栈是否为空
    bool stack_IsFull() = SWLOW;
    // 判断栈是否已满
    void stack_push(int value) = SWLOW;
    // 向栈中压入值
    void stack_push(int value, int top) {
        if (stack_isFull()) {
        throw overflow_error("栈满,无法添加");
        }
        stack_buffer[++top] = value;
    }
    301/代码"""

    cleaned = clean_ocr_edges_only(final_code)
    print(cleaned)