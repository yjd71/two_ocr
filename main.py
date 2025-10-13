import requests
import json
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

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
        生成评分提示词模板 - 修改版

        Args:
            requirements: 作业要求描述

        Returns:
            格式化后的提示词
        """
        prompt = f"""
作为C++编程教师，请根据以下要求对学生的C++代码进行评分：

作业要求:
{requirements}

评分标准:
1. 代码正确性 (60%): 代码是否能正确编译运行，是否实现要求的功能。
2. 代码规范性 (20%): 代码格式是否规范，命名是否清晰，注释是否恰当,如没有重大问题应当给与满分
3. 代码效率 (10%): 代码的时间复杂度和空间复杂度是否合理
4. 代码可读性 (10%): 代码结构是否清晰，是否易于理解

重要说明:
- 如果代码完全没有错误且完美实现要求的功能，请给予100分满分
- 不需要考虑创新性因素，只需评估代码是否正确实现要求
- 对于没有错误的代码，即使规范性、效率或可读性有轻微不足，也应给予高分

请以JSON格式返回评分结果，包含以下字段:
- score: 总分(0-100)
- breakdown: 各维度得分(包含correctness, standardization, efficiency, readability)
- reason: 评分理由，如果有语法编译错误请一定一定要具体指出说明，如缺少分号等等
- suggestions: 改进建议列表(即使满分也可以提供优化建议)，着重写出代码中具体的语法错误(如果没有就不要写)
- strengths: 代码优点列表
- weaknesses: 代码缺点列表

请确保返回的内容是有效的JSON格式，不要包含其他额外文本。
        """
        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def score_cpp_code(self, code: str, requirements: str) -> Dict[str, Any]:
        """
        使用KIMI API对C++代码进行评分

        Args:
            code: 需要评分的C++代码
            requirements: 作业要求描述

        Returns:
            包含评分结果的字典
        """
        # 构建评分提示词
        prompt = self.generate_scoring_prompt(requirements)

        # 准备API请求
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的C++编程教师，负责对学生提交的C++代码作业进行评分和分析。请确保返回有效的JSON格式，不要包含其他额外文本。"
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n需要评分的代码:\n```cpp\n{code}\n```"
                }
            ],
            "temperature": 0.1,  # 低温度确保评分一致性
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
        从API响应中提取JSON数据

        Args:
            content: API返回的内容

        Returns:
            解析后的JSON字典
        """
        try:
            # 尝试从代码块中提取JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "{" in content and "}" in content:
                # 尝试提取大括号内的JSON
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
            else:
                # 如果没有明显的JSON标记，使用整个内容
                json_str = content

            # 解析JSON
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON失败: {e}")
            return {
                "score": 0,
                "reason": "无法解析评分结果",
                "suggestions": ["请检查代码格式或重新提交"],
                "error": str(e)
            }


# 使用示例
def main():
    # 使用您的KIMI API密钥
    api_key = "sk-AKRioPFeI74AGxRBwNoSh4BQZkJSv43ommpFrLpx5yYh9zRQ"

    # 创建评分器实例
    scorer = KimiCppScorer(api_key)

    # 完全正确的C++代码
    perfect_code = """
    #include <iostream>
using namespace std;

class Stack {
    int top; // 错误：应该是private
    int array[100]; // 错误：硬编码大小

public:
    Stack() {
        top = 0; // 错误：应该初始化为-1或0取决于实现
    }

    void push(int value) {
        array[top] = value;
        top++; // 错误：没有检查是否越界
    }

    int pop() {
        top--; // 错误：先减后取，可能导致越界
        return array[top];
    }

    // 缺少isEmpty和isFull方法
    // 缺少peek方法

    void print() {
        for (int i = 0; i < top; i++) {
            cout << array[i] << " ";
        }
        cout << endl;
    }
};

int main() {
    Stack s;

    s.push(10);
    s.push(20);
    s.push(30);

    s.print();

    cout << "Popped: " << s.pop() << endl;
    cout << "Popped: " << s.pop() << endl;
    cout << "Popped: " << s.pop() << endl;
    cout << "Popped: " << s.pop() << endl; // 这里会访问非法内存

    return 0;
}
    """

    requirements = "实现栈的几种基本功能，包括push(入栈)、pop(出栈)、top(获取栈顶元素)、isEmpty(判断栈是否为空)、isFull(判断栈是否已满)。"

    print("正在对C++代码进行评分...")
    result = scorer.score_cpp_code(perfect_code, requirements)
    print("评分结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()