# 数据库配置
DATABASE = {
    "DB_USER": "postgres",
    "DB_PASSWORD": "20030701",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "two_ocr"
}

# 应用配置
app = {
    "host": "127.0.0.1",
    "port": 8000,
    "local_static_url_path": r"C:\IT\AI\OCR\two_ocr\uploads",  # 静态 URL
    "static_url_path": "http://127.0.0.1:8000/"  # 静态 URL
}

# 第三方 ai 的 API-KEY
API_KEY = "3f2dd13de7aa4475b21378c4eb5889d7"

# 本地部署的deepseek-ocr模型地址
model_name_path = "C:/IT/AI/OCR/huggingface_deepseek_ocr_model/DeepSeek-OCR"
output_path = './output'  # 输出保存地址

# 初始图片保存目录
img_upload_dir = "C:/IT/AI/OCR/two_ocr/uploads/original_image"

# 预处理图片保存目录
image_processed_path = "C:/IT/AI/OCR/two_ocr/uploads/processed_image/"
