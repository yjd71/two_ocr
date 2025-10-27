from two_ocr.src.AI_report import ai
from fastapi import FastAPI, HTTPException,APIRouter
from two_ocr.common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

# 创建路由实例，添加API前缀和标签
router = APIRouter()



@router.post("/api/assignments/{assignmentId}/report")
async def AI_api(assignmentId: str):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
        OCR图片识别接口，基于作业ID查询并处理图片。

        :param assignmentId: 作业ID，由前端提供
        :return: 包含OCR识别结果的响应
        """
    # print("ocr_api运行成功:",assignmentId)
    # return success_response(data={"recognizedCode":assignmentId})


    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, str):
            return validation_error_response(message="作业ID无效")

        """ 根据作业ID查找数据库中作业 """


        """ 调用大模型进行评分，返回评分结果 """
        perfect_code = """

            #include <iostream>
            #include <vector>
            using namespace std;

            template<typename T>
            class AdvancedStack {
            private:
                vector<T> elements;
                int maxSize;

            public:
                AdvancedStack(int size = 100) : maxSize(size) {}

                void push(T value) {
                    if (elements.size() >= maxSize) {
                        throw runtime_error("Stack overflow!");
                    }
                    elements.push_back(value);
                }

                T pop() {
                    if (elements.empty()) {
                        throw runtime_error("Stack underflow!");
                    }
                    T value = elements.back();
                    elements.pop_back();
                    return value;
                }

                T peek() {
                    if (elements.empty()) {
                        throw runtime_error("Stack is empty!");
                    }
                    return elements.back();
                }

                bool isEmpty() {
                    return elements.empty();
                }

                bool isFull() {
                    return elements.size() >= maxSize;
                }

                // 问题：使用vector而不是数组，但maxSize限制可能不准确
                // vector会自动扩容，这与栈的固定大小概念不符

                void display() {
                    cout << "Stack contents: ";
                    for (auto it = elements.rbegin(); it != elements.rend(); ++it) {
                        cout << *it << " ";
                    }
                    cout << endl;
                }
            };

            int main() {
                try {
                    AdvancedStack<int> stack(3);

                    stack.push(1);
                    stack.push(2);
                    stack.push(3);
                    stack.display();

                    stack.push(4); // 这里会抛出异常
                }
                catch (const exception& e) {
                    cout << "Exception: " << e.what() << endl;
                }

                return 0;
            }
                """
        results = ai.ai(perfect_code)
        if results is None:
            return service_error_response(message="AI调用失败")

        """ 将输出结果保存在数据库中 """

        # 返回成功响应
        return success_response(data={
                                      "score": results["score"],
                                      "breakdown":{
                                          "correctness":results["breakdown"]["correctness"],
                                          "standardization":results["breakdown"]["standardization"],
                                          "efficiency":results["breakdown"]["efficiency"],
                                          "readability":results["breakdown"]["readability"],
                                          },
                                      "reason":results["reason"],
                                      "suggestions":results["suggestions"],
                                      "strengths":results["strengths"],
                                      "weaknesses":results["weaknesses"],
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message="服务器内部错误")



