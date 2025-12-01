# run_cpp_wandbox_strict_multiline.py
# 用途：把 C++ 源码提交到 Wandbox，并将编译/运行错误以原始多行文本保存在 data["error"]
# 需要：pip install requests

import requests
import time
import json
from typing import Optional

WANDBOX_URL = "https://wandbox.org/api/compile.json"


def now_str() -> str:
    """返回当前时间字符串（YYYY-MM-DD HH:mm:ss）"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def run_cpp_wandbox_strict_multiline(code: str, compiler: str = "gcc-head", timeout: int = 15) -> dict:
    """
    提交 code 到 Wandbox 并返回严格的 data 对象（字段与类型按要求）。
    与之前的函数不同点：error 字段保留原始多行输出（不做 strip / 合并为一行）。
    评分规则（硬编码）：
      - 编译失败：score = 0
      - 编译成功且运行返回码 == 0：score = 100
      - 编译成功但运行超时：score = 20
      - 编译成功但运行返回码 != 0：score = 60
    """
    submit_time = now_str()
    code_bytes = code.encode("utf-8")
    code_len = len(code_bytes)

    """
        参数：
          - code: 要执行的 C++ 源代码（字符串）
          - compiler: 要使用的编译器标识（例如 "gcc-head", "clang-head" 等）
          - timeout: 网络请求超时时间（秒）
        返回：
          - dict: Wandbox 返回的 JSON（已解析）
    """
    payload = {
        "code": code,
        "compiler": compiler
    }

    # 发送请求
    try:
        resp = requests.post(WANDBOX_URL, json=payload, timeout=timeout)
    except requests.RequestException as e:
        eval_time = now_str()
        return {
            "language": "C++",
            "codeLengthBytes": int(code_len),
            "submitTime": submit_time,
            "evalTime": eval_time,
            "compileSuccess": False,
            "output": None,
            # 把请求异常消息放到 error 中（多行也可）
            "error": f"网络请求失败: {e}",
            "score": 0
        }

    eval_time = now_str()

    # 解析返回 JSON（若非 JSON 则把原文保存在 error 中）
    try:
        j = resp.json()
    except Exception:
        return {
            "language": "C++",
            "codeLengthBytes": int(code_len),
            "submitTime": submit_time,
            "evalTime": eval_time,
            "compileSuccess": False,
            "output": None,
            "error": f"Wandbox 返回非 JSON 内容:\n{resp.text}",
            "score": 0
        }

    # 取出可能的字段（保留原始多行，不做 strip）
    compiler_message_raw = j.get("compiler_message") or j.get("compiler_output") or j.get("compiler_error") or ""
    program_output_raw = j.get("program_output") or j.get("program_message") or j.get("program_error") or ""
    status_raw = j.get("status")  # 可能为数字或字符串
    signal = j.get("signal")

    # 用一个小副本用于检测（lower-case），但不影响原始文本的保留
    comp_lower = compiler_message_raw.lower() if compiler_message_raw else ""
    error_indicators = ("error:", "undefined reference", "compilation terminated", "fatal error", "error ")

    # 判断是否为编译错误（仅用于判定 compileSuccess），但不要修改 compiler_message_raw
    compile_success = True
    if comp_lower and any(ind in comp_lower for ind in error_indicators):
        compile_success = False

    # 额外判断：如果没有 compiler 信息但有 program 输出或 status，通常视作编译成功并已运行
    if not compiler_message_raw and (program_output_raw or status_raw is not None):
        compile_success = True

    # 准备 output/error（保留多行原始文本或 None）
    output_str: Optional[str] = program_output_raw if program_output_raw != "" else None
    error_str: Optional[str] = None
    score = 0

    if not compile_success:
        # 编译失败：将编译器原始输出（可能多行）作为 error 返回
        error_str = compiler_message_raw if compiler_message_raw != "" else "Compilation failed (no further info)."
        output_str = None
        score = 0
    else:
        # 编译成功：判断运行结果
        exit_code = None
        try:
            if status_raw is not None and str(status_raw).strip() != "":
                exit_code = int(status_raw)
        except Exception:
            exit_code = None

        if signal:
            # 有 signal，表明异常终止（保留 signal 与任何 program 输出）
            # 把 signal 信息与 program 输出合并成多行 error
            pieces = [f"Terminated by signal: {signal}"]
            if program_output_raw:
                pieces.append("Program output / message:\n" + program_output_raw)
            error_str = "\n".join(pieces)
            score = 20
        else:
            if exit_code is None:
                # 无明确 exit code 的情况：若有 program_output，认为运行成功（宽松处理）
                if output_str is None:
                    # 无输出，默认认为程序成功退出
                    score = 100
                else:
                    score = 100
            else:
                # 有明确退出码
                if exit_code == 0:
                    score = 100
                else:
                    score = 60
                    # 运行非零时，把 program 输出/错误作为 error（保留多行）
                    if program_output_raw:
                        error_str = program_output_raw
                    else:
                        # 若 program 无输出，可把编译信息（若有）也附带
                        if compiler_message_raw:
                            error_str = compiler_message_raw
                        else:
                            error_str = f"Program exited with code {exit_code} (no further output)."

    # 若最终没有 error_str 且 program_error 字段存在，使用之（保留原样）
    if error_str is None and j.get("program_error"):
        pe = j.get("program_error")
        error_str = pe if pe != "" else None

    # 构建严格的返回对象
    data = {
        "language": "C++",
        "codeLengthBytes": int(code_len),
        "submitTime": submit_time,
        "evalTime": eval_time,
        "compileSuccess": bool(compile_success),
        # output / error 必须是 string 或 null
        "output": output_str,
        "error": error_str,
        "score": int(score)
    }

    return data


def compile_run(code, compiler, timeout):
    result = run_cpp_wandbox_strict_multiline(code, compiler=compiler, timeout=timeout)
    # 把整个返回 转成 JSON 格式
    # result = json.dumps(result, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    # 测试用例：可直接改为任意 C++ 源码
    sample_code_my = r'''
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
    sample_bad = r'''
    #include <iostream>
    using namespace std;
    class Stack {
    private:
        int& elements; // 故意的错误：引用不能指向 new 返回的指针，用于演示编译错误格式
        int top;
        int maxSize;
    public:
        Stack(int size = 5){
            maxSize = size;
            elements = new int[maxSize];
            top = -1;
        }
    };
    int main() {
        return 0;
    }
    '''
    sample = r'''
    #include <iostream>
    int main() {
        std::cout << "Hello, Wandbox strict format!" << std::endl;
        return 0;
    }
    '''
    sample_score_60 = r'''
        #include <iostream>
        int main() {
            int x = 1;
            int y = 0;
            std::cout << "Before crash..." << std::endl;
            int z = x / y;  // 运行时错误：除以 0
            return 0;
        }
        '''
    """
        参数：
          - code: 要执行的 C++ 源代码（字符串）
          - compiler: 要使用的编译器标识（例如 "gcc-head", "clang-head" 等）
          - timeout: 网络请求超时时间（秒）
        返回：
          - dict: Wandbox 返回的 JSON（已解析）
    """
    res = compile_run(sample_code_my, compiler="gcc-head", timeout=20)
    result = json.dumps(res, ensure_ascii=False, indent=2)
    print(result)
