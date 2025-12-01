import re
import json
from datetime import datetime


class MockCppCompiler:
    def __init__(self):
        self.common_errors = [
            "expected ';' before 'return'",
            "expected ';' after expression",
            "expected primary-expression before '}' token",
            "missing terminating character",
            "undefined reference to",
            "cout was not declared in this scope",
            "iostream: No such file or directory"
        ]

    def compile_and_run(self, source_code):
        """
        模拟编译并运行C++源代码

        Args:
            source_code (str): OCR识别到的C++源代码文本（含换行符）

        Returns:
            dict: 包含模拟编译和执行结果的字典
        """
        # 初始化响应结构
        response = {
            "code": 0,
            "message": "成功",
            "data": {
                "language": "C++",
                "codeLengthBytes": len(source_code.encode('utf-8')),
                "submitTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "evalTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "compileSuccess": False,
                "output": None,
                "error": None,
                "score": 0  # 添加评分字段
            }
        }

        # 分析代码并模拟编译结果
        compile_success, output, error, score = self._analyze_code(source_code)

        response["data"]["compileSuccess"] = compile_success
        response["data"]["score"] = score

        if compile_success:
            response["data"]["output"] = output
        else:
            response["data"]["error"] = error
            # 如果编译失败，设置相应的错误码和消息
            response["code"] = 1
            response["message"] = "编译失败"

        return response

    def _analyze_code(self, source_code):
        """
        分析C++代码并模拟编译和执行结果
        """
        # 检查常见语法错误
        syntax_errors = self._check_syntax_errors(source_code)
        if syntax_errors:
            return False, None, syntax_errors, 0  # 编译失败，分数为0

        # 计算分数
        score = self._calculate_score(source_code)

        # 检查是否能输出Hello World
        if self._contains_hello_world(source_code):
            return True, "Hello, World!\n", None, score

        # 检查是否有输出语句
        output = self._simulate_output(source_code)
        if output:
            return True, output, None, score

        # 默认情况：编译成功但无输出
        return True, "", None, score

    def _calculate_score(self, source_code):
        """
        根据代码质量计算分数
        评分规则：
        - 基础分：编译成功得50分
        - 包含main函数：+20分
        - 包含正确的头文件：+10分
        - 包含return语句：+10分
        - 输出Hello World：+10分
        - 代码格式规范（有适当的缩进和换行）：+10分
        """
        score = 0

        # 基础分：编译成功
        score += 50

        # 检查main函数
        if "int main" in source_code or "void main" in source_code:
            score += 20

        # 检查头文件
        if "#include" in source_code:
            score += 10

        # 检查return语句
        if "return" in source_code:
            score += 10

        # 检查是否输出Hello World
        if self._contains_hello_world(source_code):
            score += 10

        # 检查代码格式（简单的缩进检查）
        lines = source_code.split('\n')
        indented_lines = sum(1 for line in lines if line.strip() and line.startswith('    '))
        if indented_lines > len(lines) * 0.3:  # 如果30%以上的非空行有缩进
            score += 10

        # 确保分数不超过100
        return min(score, 100)

    def _check_syntax_errors(self, source_code):
        """检查常见语法错误"""
        lines = source_code.split('\n')

        # 检查是否缺少分号
        for i, line in enumerate(lines):
            line = line.strip()
            # 跳过空行、预处理指令、注释和块开始/结束
            if (not line or
                    line.startswith('#') or
                    line.startswith('//') or
                    line.startswith('/*') or
                    line.endswith('{') or
                    line.endswith('}') or
                    line.startswith('}') or
                    'if (' in line or
                    'for (' in line or
                    'while (' in line or
                    line.endswith(') {') or
                    line.startswith('int main') or
                    line.startswith('void main') or
                    line.startswith('class ') or
                    line.startswith('struct ')):
                continue

            # 检查是否应该以分号结尾但没有
            if (not line.endswith(';') and
                    not line.endswith('{') and
                    not line.endswith('}') and
                    not line.startswith('namespace') and
                    not line.startswith('using namespace') and
                    not line.startswith('return ') and
                    not line.startswith('#include')):
                return f"main.cpp:{i + 1}: error: expected ';' before '}}' token"

        # 检查是否包含必要的头文件和main函数
        if "#include" not in source_code and "cout" in source_code:
            return "main.cpp: error: 'cout' was not declared in this scope"

        if "int main" not in source_code and "void main" not in source_code:
            return "main.cpp: error: undefined reference to `main'"

        return None

    def _contains_hello_world(self, source_code):
        """检查代码是否输出Hello World"""
        hello_patterns = [
            r'cout\s*<<\s*"Hello,\s*World!"',
            r'printf\s*\(\s*"Hello,\s*World!"',
            r'std::cout\s*<<\s*"Hello,\s*World!"',
            r'"Hello,\s*World!"'
        ]

        for pattern in hello_patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                return True
        return False

    def _simulate_output(self, source_code):
        """模拟代码输出"""
        # 查找输出语句
        output_patterns = [
            r'cout\s*<<\s*"([^"]*)"',
            r'printf\s*\(\s*"([^"]*)"',
            r'std::cout\s*<<\s*"([^"]*)"'
        ]

        for pattern in output_patterns:
            match = re.search(pattern, source_code)
            if match:
                output_text = match.group(1)
                # 处理转义字符
                output_text = output_text.replace('\\n', '\n')
                output_text = output_text.replace('\\t', '\t')
                return output_text + '\n'

        return None


# 使用示例和测试
def compile_run(success_code):
    compiler = MockCppCompiler()
    result = compiler.compile_and_run(success_code)
    return result


if __name__ == "__main__":
    success_code = """
#include <iostream>
using namespace std;
class Stack
{
private:
    int& elements;
    int top;
    int maxSize;
public:
    Stack(int size = 5){
    maxSize = size;
    elements = new int[maxSize];
    top = -1;
    }
    ~Stack(){
    delete[] elements;
    }
    void push(int element){
    if(top < maxSize - 1){
    elements[++top] = element;
    cout << "元素" << element << "被压入栈" << endl;
    }
    else {
    cout << "栈满,无法压入栈" << endl;
    }
    }
};

int pop(){
    if(top == 0){
    int element = elements[top--];
    cout << "元素" << element << "被弹出" << endl;
    }
    else {
    cout << "栈空,无法弹出" << endl;
    }
    return 0;
};

int getSize(){
    int size = top;
    cout << "栈中当前有" << size << "个元素" << endl;
    return size;
};

int getEmptyLots(){
    int empty = maxSize - (top + 1);
    cout << "栈中已空剩" << empty << "个空位" << endl;
    return empty;
};

int main(){
    Stack stack;
    stack.push(0);
    stack.push(1);
    stack.pop();
    stack.getSize();
    stack.getEmptyLots();
    return 0;
};
    """
    result = compile_run(success_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


