import difflib  # difflib 模块，用于比较文本序列的相似度


# 智能合并两个有重叠的代码片段
def _merge_two_blocks(text_top, text_bottom, search_window=10, threshold=0.8):
    """"""
    """
      :param text_top: 上半部分的文本
      :param text_bottom: 下半部分的文本
      :param search_window: 搜索重叠的最大行数（根据10%重叠，大概是2-3行，设大点没关系）
      :param threshold: 相似度阈值 (0-1)，高于此值才认为重叠匹配成功
      :return: 合并后的文本
      """
    """
    智能合并，忽略空格和缩进差异，极大提高去重成功率
    """
    lines_top = text_top.splitlines()  # 将上半部分文本按行分割成列表
    lines_bottom = text_bottom.splitlines()  # 将下半部分文本按行分割成列表

    if not lines_top or not lines_bottom:  # 如果上半部分或下半部分的代码行列表为空
        return text_top + "\n" + text_bottom  # 直接拼接两部分文本并返回，不进行去重处理

    # 1. 确定搜索范围 (建议设为 2，确保覆盖 10% 的重叠区域)
    compare_window = min(len(lines_top), search_window)  # 计算实际比较窗口大小，取上半部分行数和预设窗口值的较小者
    check_lines_top = lines_top[-compare_window:]  # 获取上半部分文本的最后 compare_window 行，作为待比对区域

    max_overlap = min(len(check_lines_top), len(lines_bottom), search_window)  # 计算最大可能的重叠行数，受限于待比对区域长度、下半部分长度和搜索窗口大小

    best_overlap_lines = 0  # 初始化最佳重叠行数为 0
    best_ratio = 0.0  # 初始化最高相似度比率为 0.0

    # 辅助函数：标准化字符串（去除所有空格和换行，只比较核心内容）
    def normalize(s):  # 定义内部辅助函数，用于标准化字符串
        return "".join(s.split())  # 将字符串按空白字符分割后重新连接，去除所有空格、换行符等

    # 2. 倒序尝试重叠
    for i in range(max_overlap, 0, -1):  # 从最大可能的重叠行数开始倒序循环到 1
        # 取出原始文本片段
        chunk_top_raw = "\n".join(check_lines_top[-i:])  # 取出上半部分待比对区域的最后 i 行并合并为字符串
        chunk_bottom_raw = "\n".join(lines_bottom[:i])  # 取出下半部分的前 i 行并合并为字符串

        # === 核心修改：比较标准化后的字符串 ===
        # 这样 "push (&s, 10);" 和 "  push(&s, 10); " 会被视为完全相同
        seq_top = normalize(chunk_top_raw)  # 对上半部分取出的片段进行标准化处理（去空白）
        seq_bottom = normalize(chunk_bottom_raw)  # 对下半部分取出的片段进行标准化处理（去空白）

        # 如果标准化后内容太短（比如只是一个 "}"），容易误判，跳过
        if len(seq_top) < 5:  # 如果标准化后的内容长度小于 5 个字符
            continue  # 跳过本次循环，尝试下一个重叠行数

        """
        原理：寻找最长的连续共同子串：ratio = 2*M / T
            M (Matches)：所有匹配片段的字符总数。
            T (Total)：两个字符串长度的总和（len(seq_top) + len(seq_bottom)）。
        """
        ratio = difflib.SequenceMatcher(None, seq_top, seq_bottom).ratio()  # 计算两个标准化字符串的相似度比率 (0.0 到 1.0)

        # 调试打印（看到真实的相似度）
        # print(f"  比对行数: {i}, 标准化相似度: {ratio:.4f}")

        if ratio > best_ratio:  # 如果当前计算的相似度大于之前记录的最高相似度
            best_ratio = ratio  # 更新最高相似度
            best_overlap_lines = i  # 更新对应的最佳重叠行数

        # 如果标准化后几乎完全一致，直接中断
        if ratio > 0.98:  # 如果相似度超过 0.98（几乎完全一致）
            break  # 认为找到最佳匹配，提前结束循环

    # 3. 判断合并
    # 阈值建议 0.6 - 0.7 即可，因为我们要容忍 OCR 把 '.' 识别成 ',' 这种微小错误
    if best_ratio > threshold:  # 如果找到的最高相似度大于设定的阈值
        print(f"  >>> 成功去重合并! 重叠行数: {best_overlap_lines} (相似度: {best_ratio:.2f})")  # 打印成功合并的信息，包括重叠行数和相似度
        merged_lines = lines_top + lines_bottom[best_overlap_lines:]  # 构建合并后的行列表：上半部分全部 + 下半部分去除重叠后的剩余部分
        return "\n".join(merged_lines)  # 将合并后的行列表用换行符连接并返回
    else:  # 如果相似度未达到阈值
        print(f"  XXX 未检测到重叠 (最高相似度 {best_ratio:.2f})，直接拼接")  # 打印未检测到重叠的提示信息
        return text_top + "\n" + text_bottom  # 直接拼接上下两部分文本并返回


# 主入口函数，于批量合并文本块列表v
def smart_merge(text_blocks, search_window=10, threshold=0.8):
    # 参数：text_blocks(文本块列表), search_window(搜索窗口), threshold(阈值)

    if not text_blocks: return ""  # 如果文本块列表为空，返回空字符串
    if len(text_blocks) == 1: return text_blocks[0]  # 如果列表只有一个文本块，直接返回该文本块

    print(f"开始智能合并 {len(text_blocks)} 个切片...")  # 打印日志，显示即将合并的切片数量
    current_merged_text = text_blocks[0]  # 初始化当前合并结果为列表中的第一个文本块

    for i in range(1, len(text_blocks)):  # 从列表的第二个元素开始遍历剩余文本块
        current_merged_text = _merge_two_blocks(  # 调用 _merge_two_blocks 函数进行累积合并
            current_merged_text,  # 当前已合并的文本作为上半部分
            text_blocks[i],  # 当前遍历到的文本块作为下半部分
            search_window=search_window,  # 传递搜索窗口大小参数
            threshold=threshold  # 传递相似度阈值参数
        )
    return current_merged_text  # 返回最终合并完成的文本
