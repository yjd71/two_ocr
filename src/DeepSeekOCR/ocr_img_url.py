##################################################################################################
# 在本节中，我们将设置用户身份验证、用户和应用程序 ID、模型详细信息以及我们想要作为输入的图像的 URL。
# 更改这些字符串以运行您自己的示例。
#################################################################################################
import base64
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import cv2

# Your PAT (Personal Access Token) can be found in the Account's Security section
PAT = '3f2dd13de7aa4475b21378c4eb5889d7'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'deepseek-ai'
APP_ID = 'deepseek-ocr'
# Change these to whatever model and image URL you want to use
MODEL_ID = 'DeepSeek-OCR'
MODEL_VERSION_ID = '517c2d5e100b48ffb224bd29c961d128'
IMAGE_URL = 'https://static001.geekbang.org/infoq/b9/b9fa32594f625a6e4af7d77a2daa8700.png'
# IMAGE_URL = 'http://127.0.0.1:8000/uploads/original_image/IMG_20250928_220327.jpg'

# 添加必要的提示
PROMPT_TEXT = "识别图片中的手写体代码"

############################################################################
# 您无需更改此行以下的任何内容即可运行此示例
############################################################################


channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

post_model_outputs_response = stub.PostModelOutputs(
    service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
        model_id=MODEL_ID,
        version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        url=IMAGE_URL
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
output = post_model_outputs_response.outputs[0]

print("Predicted concepts:")
for concept in output.data.concepts:
    print("%s %.2f" % (concept.name, concept.value))

# Uncomment this line to print the full Response JSON
print(output)

# 打印结果

text_content = output.data.string_value

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
print(f"提示令牌数: {output.prompt_tokens}")
print(f"完成令牌数: {output.completion_tokens}")