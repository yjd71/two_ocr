import base64
import http.client
import json
import os

# 本地图片路径
LOCAL_IMAGE_PATH = '../../Data/241042Y438/test1/IMG_20250928_220351.jpg'


# 将本地图片转换为base64编码的字节数据
def image_to_base64_bytes(LOCAL_IMAGE_PATH):
    # 检查图片文件是否存在
    if not os.path.exists(LOCAL_IMAGE_PATH):
        raise FileNotFoundError(f"图片文件不存在: {LOCAL_IMAGE_PATH}")

    """将本地图片转换为base64编码的字节数据"""
    with open(LOCAL_IMAGE_PATH, "rb") as image_file:
        return base64.b64encode(image_file.read())  # 不移除 .decode('utf-8')


image_base64_bytes = image_to_base64_bytes(LOCAL_IMAGE_PATH)
image_base64_bytes = f'{image_base64_bytes}'

conn = http.client.HTTPSConnection("api.chatanywhere.tech")
payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "你是一个ocr识别的人工智能，我只会给你一个手写体的代码的base64编码的字节数据，你需要从中识别出代码，进行输出"
        },
        {
            "role": "user",
            "content": image_base64_bytes
        }
    ]
})
headers = {
    'Authorization': 'sk-RIoTkpmtU8AdISSVWFPARmjCC4lOdQM4Lz5yHlpaJCmBWDAE',
    'Content-Type': 'application/json'
}
conn.request("POST", "/v1/chat/completions", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
