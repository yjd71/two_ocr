##################################################################################################
# 设置用户身份验证、用户和应用程序 ID、模型详细信息以及想要作为输入的图像。
#################################################################################################
import base64
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import os

# Your PAT (Personal Access Token) can be found in the Account's Security section
PAT = '3f2dd13de7aa4475b21378c4eb5889d7'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'deepseek-ai'
APP_ID = 'deepseek-ocr'
# Change these to whatever model and image URL you want to use
MODEL_ID = 'DeepSeek-OCR'
MODEL_VERSION_ID = '517c2d5e100b48ffb224bd29c961d128'

# 添加必要的提示
PROMPT_TEXT = "识别图片中的手写体代码"


# 将本地图片转换为base64编码的字节数据
def image_to_base64_bytes(LOCAL_IMAGE_PATH):
    # 检查图片文件是否存在
    if not os.path.exists(LOCAL_IMAGE_PATH):
        raise FileNotFoundError(f"图片文件不存在: {LOCAL_IMAGE_PATH}")

    """将本地图片转换为base64编码的字节数据"""
    with open(LOCAL_IMAGE_PATH, "rb") as image_file:
        return base64.b64encode(image_file.read())  # 不移除 .decode('utf-8')


# deepseek ocr api
def deepseek_ocr(LOCAL_IMAGE_PATH):
    # 将本地图片转换为base64编码的字节数据
    image_base64_bytes = image_to_base64_bytes(LOCAL_IMAGE_PATH)

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=image_base64_bytes  # 直接传递字节数据
                        ),
                        # 添加必需的文本提示
                        text=resources_pb2.Text(
                            raw=PROMPT_TEXT
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )

    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here
    print(post_model_outputs_response)
    print("═" * 60)
    output = post_model_outputs_response.outputs[0]
    # 打印完整的响应 JSON
    # print(output)

    # 具体识别内容
    result = output.data.string_value
    return result


if __name__ == '__main__':
    # 本地图片路径
    LOCAL_IMAGE_PATH = '../../Data/241042Y438/test1/IMG_20250928_220351.jpg'

    # 调用deepseek api
    text_content = deepseek_ocr(LOCAL_IMAGE_PATH)

    # 打印结果
    print("OCR识别结果详情:")
    print("═" * 60)
    print(f"总行数: {len(text_content.splitlines())}")
    print(f"总字符数: {len(text_content)}")
    print("═" * 60)

    lines = text_content.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():  # 只显示非空行
            print(f"{i:2d}. {line}")

    print("═" * 60)
