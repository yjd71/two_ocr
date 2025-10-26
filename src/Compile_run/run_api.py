import re
from datetime import datetime
import json



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
            "data": {
                "language": "C++",
                "codeLengthBytes": len(source_code.encode('utf-8')),
                "submitTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "evalTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "compileSuccess": False,
                "output": None,
                "error": None,
            }
        }

        # 分析代码并模拟编译结果
        compile_success, output, error = self._analyze_code(source_code)

        response["data"]["compileSuccess"] = compile_success
        if compile_success:
            response["data"]["output"] = output
        else:
            response["data"]["error"] = error

        return response

    def _analyze_code(self, source_code):
        """
        分析C++代码并模拟编译和执行结果
        """
        # 检查常见语法错误
        syntax_errors = self._check_syntax_errors(source_code)
        if syntax_errors:
            return False, None, syntax_errors

        # 检查是否能输出Hello World
        if self._contains_hello_world(source_code):
            return True, "Hello, World!\n", None

        # 检查是否有输出语句
        output = self._simulate_output(source_code)
        if output:
            return True, output, None

        # 默认情况：编译成功但无输出
        return True, "", None

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

    # 测试成功案例 - Hello World

    result = compiler.compile_and_run(success_code)
    return result






if __name__ == "__main__":
    success_code = """#include <iostream>
    using namespace std;
    int main() {
        cout << "Hello, World!" << endl;
        return 0;
    }
    """
    result=compile_run(success_code)
    # var = result["data"]["language"]
    # print(var)
    print(json.dumps(result, indent=2, ensure_ascii=False))


