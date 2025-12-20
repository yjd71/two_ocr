import requests
import json
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging
import json_repair # 专门用于修复 LLM（大模型）生成的损坏 JSON 的库。它可以自动处理缺失的逗号、未转义的引号等问题。

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KimiCppScorer:
    def __init__(self, api_key: str):
        """
        初始化KIMI C++代码评分器

        Args:
            api_key: KIMI API密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.moonshot.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_scoring_prompt(self, requirements: str) -> str:
        """
        生成评分提示词模板 - OCR场景优化版

        Args:
            requirements: 作业要求描述

        Returns:
            格式化后的提示词
        """
        prompt = f"""
                    作为C++编程教师，你正在评分由OCR识别的手写代码作业。
                    
                    【重要背景】
                    - 这些代码是从学生手写作业中通过OCR识别得到的
                    - OCR识别可能存在错误（如字符识别错误、符号混淆等）
                    - 编译失败通常是由OCR识别错误导致，而非学生的编程逻辑错误
                    - 你需要透过OCR错误，评估学生的真实编程能力和算法思路
                    
                    作业要求:
                    {requirements}
                    
                    【评分原则】
                    核心思想：**重点评估代码逻辑和算法思路，而非编译错误**
                    
                    1. **区分OCR错误和逻辑错误**
                       - OCR常见错误：字符识别错误(0/O, 1/l/I)、符号错误(;/,)、关键字拼写错误等
                       - 逻辑错误：算法思路错误、数据结构使用不当、边界条件处理错误等
                       - **OCR错误不应大幅降低正确性分数**
                    
                    2. **评分重点**
                       - ✅ 算法思路是否正确
                       - ✅ 数据结构选择是否合理
                       - ✅ 关键逻辑是否完整（如栈的push/pop操作）
                       - ✅ 边界条件是否考虑（如栈满、栈空判断）
                       - ⚠️ 编译错误仅作为参考，不作为主要扣分依据
                    
                    3. **如何利用编译错误信息**
                       - 编译错误可以帮助理解代码意图
                       - 通过错误信息推断学生的原始代码逻辑
                       - 在suggestions中指出可能的OCR识别问题
                    
                    评分维度和标准(每个维度满分100分):
                    
                    1. 代码正确性 (correctness, 权重60%):
                       - 90-100分: 算法逻辑完全正确，数据结构使用恰当，边界条件完整，即使有OCR错误
                       - 75-89分: 算法逻辑基本正确，主要功能完整，可能缺少部分边界条件处理
                       - 60-74分: 算法思路正确，但实现不够完整，或有部分逻辑错误
                       - 45-59分: 能看出基本的算法思路，但实现有明显缺陷
                       - 30-44分: 包含部分正确的代码片段，但整体逻辑混乱
                       - 15-29分: 代码与要求相关，但几乎没有正确的逻辑
                       - 0-14分: 完全不相关或无法理解代码意图
                    
                    2. 代码规范性 (standardization, 权重20%):
                       - 90-100分: 命名规范，代码结构清晰，符合C++编码规范
                       - 75-89分: 基本规范，有少量格式问题
                       - 60-74分: 部分规范，存在一些命名或格式问题
                       - 45-59分: 规范性一般，但代码结构基本可读
                       - 30-44分: 规范性较差，但能看出代码结构
                       - 0-29分: 几乎没有规范性
                    
                    3. 代码效率 (efficiency, 权重10%):
                       - 90-100分: 算法高效，时间空间复杂度优秀
                       - 75-89分: 算法合理，效率良好
                       - 60-74分: 算法可行，效率中等
                       - 45-59分: 算法可行但效率较低
                       - 0-44分: 算法效率很差或不合理
                    
                    4. 代码可读性 (readability, 权重10%):
                       - 90-100分: 代码清晰易懂，逻辑流畅
                       - 75-89分: 代码较清晰，基本易懂
                       - 60-74分: 代码可读，需要一定理解成本
                       - 45-59分: 代码较难理解但逻辑可追踪
                       - 0-44分: 代码混乱难懂
                    
                    【评分示例】
                    例如：栈的实现代码，编译失败但包含完整的push/pop/top逻辑和栈满栈空判断
                    - 正确性：80-90分（逻辑完整正确，编译错误可能是OCR导致）
                    - 规范性：70-80分（命名和结构合理）
                    - 效率：80-90分（数组实现栈，效率良好）
                    - 可读性：75-85分（逻辑清晰）
                    - 总分：约78-88分
                    
                    总分计算公式:
                    score = correctness × 0.6 + standardization × 0.2 + efficiency × 0.1 + readability × 0.1
                    
                    请以JSON格式返回评分结果，包含以下字段:
                    - score: 总分(0-100)，必须等于各维度加权和，四舍五入到整数
                    - breakdown: 各维度得分对象，包含correctness, standardization, efficiency, readability四个字段
                    - reason: 评分理由(150-250字)，重点说明：
                      * 代码的算法逻辑是否正确
                      * 哪些是OCR错误，哪些是真正的逻辑问题
                      * 各维度分数的具体依据
                    - strengths: 代码优点列表(数组，2-4条)，重点突出算法思路和逻辑正确的地方
                    - weaknesses: 代码缺点列表(数组，2-4条)，区分OCR错误和真正的逻辑错误
                    - suggestions: 改进建议列表(数组，2-4条)，包括：
                      * 可能的OCR识别错误及修正建议
                      * 真正需要改进的逻辑问题
                      * 代码优化建议
                    
                    请确保返回的内容是有效的JSON格式，不要包含其他额外文本。
                            """
        return prompt

    def _parse_run_result(self, run_result: str) -> Dict[str, Any]:
        """
        解析运行结果，提取关键信息

        Args:
            run_result: 运行结果字符串

        Returns:
            包含解析后信息的字典
        """
        try:
            # 尝试解析JSON格式的运行结果
            result_data = json.loads(run_result)
            return {
                "compile_success": result_data.get("compileSuccess", False),
                "has_error": bool(result_data.get("error")),
                "error_message": result_data.get("error", ""),
                "output": result_data.get("output"),
                "score": result_data.get("score", 0)
            }
        except:
            # 如果不是JSON格式，返回原始字符串
            return {
                "compile_success": "error" not in run_result.lower(),
                "has_error": "error" in run_result.lower(),
                "error_message": run_result,
                "output": run_result,
                "score": 0
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def score_cpp_code(self, code: str, run_result: str, requirements: str) -> Dict[str, Any]:
        """
        使用KIMI API对C++代码进行评分

        Args:
            code: 需要评分的C++代码
            run_result: 代码运行结果
            requirements: 作业要求描述

        Returns:
            包含评分结果的字典
        """
        # 解析运行结果
        parsed_result = self._parse_run_result(run_result)

        # 构建评分提示词
        prompt = self.generate_scoring_prompt(requirements)

        # 构建运行结果说明
        result_summary = f"""
                            运行结果分析:
                            - 编译状态: {'成功' if parsed_result['compile_success'] else '失败（可能是OCR识别错误导致）'}
                            - 是否有错误: {'是' if parsed_result['has_error'] else '否'}
                            """
        if parsed_result['has_error']:
            result_summary += f"""
                                【编译错误分析】
                                请注意：由于代码来自OCR识别，编译错误很可能是识别错误导致，而非学生的逻辑错误。
                                请仔细分析错误信息，推断学生的原始代码意图，重点评估算法逻辑是否正确。
                                
                                错误信息摘要: {parsed_result['error_message'][:500]}
                                """
        if parsed_result['output']:
            result_summary += f"\n- 输出结果: {parsed_result['output'][:200]}\n"

        # 准备API请求
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的C++编程教师，正在评分OCR识别的手写代码作业。
                                关键原则：
                                1. 重点评估学生的算法思路和编程逻辑，而非编译错误
                                2. 编译失败通常是OCR识别错误，不应作为主要扣分依据
                                3. 透过OCR错误，理解学生的真实编程能力
                                4. 给出公正、合理的分数，既不过于严格也不过于宽松
                                请确保返回有效的JSON格式，不要包含其他额外文本。"""
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n需要评分的代码:\n```cpp\n{code}\n```\n\n{result_summary}\n\n完整运行结果:\n{run_result}"
                }
            ],
            "temperature": 0.3,  # 适中温度，保持一定一致性但允许合理变化
            "max_tokens": 2000
        }

        try:
            logger.info("调用KIMI API进行代码评分...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            # 解析API响应
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # 提取并解析JSON格式的评分结果
            score_data = self._extract_json_from_response(content)
            logger.info("代码评分完成")
            return score_data

        except Exception as e:
            logger.error(f"评分过程中发生错误: {e}")
            return {
                "score": 0,
                "reason": "评分过程发生错误",
                "suggestions": ["请稍后重试或联系管理员"],
                "error": str(e)
            }

    def _extract_json_from_response(self, content: str) -> dict:
        """
        从API响应中提取JSON数据 - 增强版
        """
        json_str = content

        # 1. 尝试提取 Markdown 代码块中的内容
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        elif "```" in content:  # 有时候模型只写 ``` 没有 json 标记
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        elif "{" in content and "}" in content:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_str = content[json_start:json_end]

        # 2. 解析 JSON
        try:
            # 优先使用 json_repair 专门用于修复 LLM（大模型）生成的损坏 JSON 的库。它可以自动处理缺失的逗号、未转义的引号等问题。
            if json_repair:
                return json_repair.loads(json_str)
            else:
                # 备用方案：标准库解析（容易报错）
                return json.loads(json_str)
        except Exception as e:
            # 3. 如果解析失败，打印原始内容以便调试
            logger.error(f"JSON解析失败. 原始内容:\n{json_str}")
            raise e  # 抛出异常让上层捕获


# 使用示例
def ai(perfect_code, run_result):
    # 使用您的KIMI API密钥
    api_key = "sk-AKRioPFeI74AGxRBwNoSh4BQZkJSv43ommpFrLpx5yYh9zRQ"

    # 创建评分器实例
    scorer = KimiCppScorer(api_key)

    # requirements = "实现栈的几种基本功能，包括push(入栈)、pop(出栈)、top(获取栈顶元素)。"
    requirements = "需要是一段C++的代码"


    print("正在对C++代码进行评分...")
    result = scorer.score_cpp_code(perfect_code, run_result, requirements)

    return result


if __name__ == "__main__":
    # C++代码
    perfect_code = """
                    #include <iostream>
                    #include <stack>
                    using namespace std;
                    constexpr int MAX = 100;
                    int data[MAX];
                    int top = -1;
                    bool push(int x) {
                        if (top == MAX - 1) return false;
                        data[++top] = x;
                        return true;
                    }
                    bool pop(int & x) {
                        if (top == -1) return false;
                        x = data[top--];
                        return true;
                    }
                    int size() { return top + 1; }
                    int avai() { return MAX - (top + 1); }
                    
                    """

    run_result = """
                {"error": "prog.cc: In function 'bool push(int)':\nprog.cc:9:5: error: reference to 'data' is ambiguous\n    9 |     data[++top] = x;\n      |     ^~~~\nIn file included from /opt/wandbox/gcc-head/include/c++/16.0.0/string:54,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/bits/locale_classes.h:42,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/bits/ios_base.h:43,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/ios:46,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/bits/ostream.h:43,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/ostream:42,\n                 from /opt/wandbox/gcc-head/include/c++/16.0.0/iostream:43,\n                 from prog.cc:1:\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:356:5: note: candidates are: 'template<class _Tp> constexpr const _Tp* std::data(initializer_list<_Tp>)'\n  356 |     data(initializer_list<_Tp> __il) noexcept\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:346:5: note:                 'template<class _Tp, long unsigned int _Nm> constexpr _Tp* std::data(_Tp (&)[_Nm])'\n  346 |     data(_Tp (&__array)[_Nm]) noexcept\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:335:5: note:                 'template<class _Container> constexpr decltype (__cont.data()) std::data(const _Container&)'\n  335 |     data(const _Container& __cont) noexcept(noexcept(__cont.data()))\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:324:5: note:                 'template<class _Container> constexpr decltype (__cont.data()) std::data(_Container&)'\n  324 |     data(_Container& __cont) noexcept(noexcept(__cont.data()))\n      |     ^~~~\nprog.cc:5:5: note:                 'int data [100]'\n    5 | int data[MAX];\n      |     ^~~~\nprog.cc: In function 'bool pop(int&)':\nprog.cc:14:9: error: reference to 'data' is ambiguous\n   14 |     x = data[top--];\n      |         ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:356:5: note: candidates are: 'template<class _Tp> constexpr const _Tp* std::data(initializer_list<_Tp>)'\n  356 |     data(initializer_list<_Tp> __il) noexcept\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:346:5: note:                 'template<class _Tp, long unsigned int _Nm> constexpr _Tp* std::data(_Tp (&)[_Nm])'\n  346 |     data(_Tp (&__array)[_Nm]) noexcept\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:335:5: note:                 'template<class _Container> constexpr decltype (__cont.data()) std::data(const _Container&)'\n  335 |     data(const _Container& __cont) noexcept(noexcept(__cont.data()))\n      |     ^~~~\n/opt/wandbox/gcc-head/include/c++/16.0.0/bits/range_access.h:324:5: note:                 'template<class _Container> constexpr decltype (__cont.data()) std::data(_Container&)'\n  324 |     data(_Container& __cont) noexcept(noexcept(__cont.data()))\n      |     ^~~~\n | int data[MAX];\n      |     ^~~~\nprog.cc: At global scope:\n| ^~\n", "score": 0, "output": null, "evalTime": "2025-12-10 21:27:42", "language": "C++", "submitTime": "2025-12-10 21:27:30", "compileSuccess": false, "codeLengthBytes": 382}
        """
    result = ai(perfect_code, run_result)

    print("评分结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))