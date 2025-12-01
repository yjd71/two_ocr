import tempfile
import subprocess
import time
import os
import shutil
import json

def compile_and_run_cpp(code_str: str, timeout_seconds: int = 5) -> dict:
    """
    编译并运行传入的 C++ 源码字符串，返回符合要求的 data 对象（dict）。
    参数：
      - code_str: C++ 源码（字符串）
      - timeout_seconds: 运行程序时的超时时间（秒）
    返回值（dict）示例结构（字段与题目一致）：
      {
        "language": "C++",
        "codeLengthBytes": 102,
        "submitTime": "2025-10-24 21:39:50",
        "evalTime": "2025-10-24 21:39:50",
        "compileSuccess": True,
        "output": "Hello, World!\n",
        "error": None,
        "score": 100
      }
    评分规则（示例，可按需调整）：
      - 编译失败：score = 0
      - 编译成功且运行返回码 == 0：score = 100
      - 编译成功但运行超时：score = 20
      - 编译成功但运行返回码 != 0：score = 60
    注意：需要系统上安装 g++（支持 -std=c++17）。
    """

    # 时间戳
    submit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建临时目录来保存源码和可执行文件
    tmpdir = tempfile.mkdtemp(prefix="cpp_run_")
    cpp_path = os.path.join(tmpdir, "submission.cpp")
    exe_path = os.path.join(tmpdir, "submission_exec")  # 非 windows 名称也可以

    try:
        # 把源码写入文件（以二进制确保字节数正确）
        with open(cpp_path, "wb") as f:
            f.write(code_str.encode("utf-8"))

        # 计算文件字节长度
        code_length = os.path.getsize(cpp_path)

        # 编译命令（使用 g++，C++17 标准）
        compile_cmd = ["g++", "-std=c++17", "-O2", cpp_path, "-o", exe_path]

        # 执行编译
        compile_proc = subprocess.run(
            compile_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30  # 防止编译卡住，编译超时设一个较大值
        )

        compile_success = (compile_proc.returncode == 0)
        compile_stdout = compile_proc.stdout.decode("utf-8", errors="replace")
        compile_stderr = compile_proc.stderr.decode("utf-8", errors="replace")

        eval_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 结果初始化
        result_output = None
        result_error = None
        score = 0

        if not compile_success:
            # 编译失败：把编译错误作为 error 返回
            result_output = None
            # 合并 stdout/stderr（以保证关键信息不丢）
            compiled_err_msg = compile_stderr.strip() or compile_stdout.strip() or "Compile failed with unknown error."
            result_error = compiled_err_msg
            score = 0
        else:
            # 编译成功，尝试运行（带超时）
            try:
                run_proc = subprocess.run(
                    [exe_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout_seconds
                )
                run_stdout = run_proc.stdout.decode("utf-8", errors="replace")
                run_stderr = run_proc.stderr.decode("utf-8", errors="replace")

                # 填充 output / error 字段
                result_output = run_stdout if run_stdout != "" else None
                result_error = run_stderr if run_stderr != "" else None

                # 简单评分策略（可以替换为更复杂的判分逻辑）
                if run_proc.returncode == 0:
                    score = 100
                else:
                    score = 60

            except subprocess.TimeoutExpired as te:
                # 运行超时
                result_output = te.stdout.decode("utf-8", errors="replace") if te.stdout else None
                result_error = ("Program timed out after {} seconds.".format(timeout_seconds))
                score = 20

            except Exception as e:
                # 其它运行时错误（比如权限问题）
                result_output = None
                result_error = "Runtime error: " + str(e)
                score = 10

        # 构建返回对象
        data = {
            "language": "C++",
            "codeLengthBytes": int(code_length),
            "submitTime": submit_time,
            "evalTime": eval_time,
            "compileSuccess": bool(compile_success),
            "output": result_output,
            "error": result_error,
            "score": int(score)
        }

        return data

    finally:
        # 清理临时目录（确保删除可执行文件与源码）
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass


# -------------------------
# 示例调用（仅示例，实际运行会在你的机器上执行编译与运行）
if __name__ == "__main__":
    cpp_code = r'''
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
'''
    # 注意：上面的 C++ 源码里存在类型错误（int& elements = new int[...]），
    # 在大多数编译器上会导致编译失败，下面的调用只是演示 API。
    result = compile_and_run_cpp(cpp_code, timeout_seconds=3)
    print(json.dumps(result, ensure_ascii=False, indent=2))
