# global_models.py
from transformers import AutoModel, AutoTokenizer
import torch
import os
from config import model_name_path


class GlobalModels:
    _instance = None
    _ocr_model = None
    _ocr_tokenizer = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalModels, cls).__new__(cls)
        return cls._instance

    def init_ocr_model(self):
        """初始化OCR模型"""
        if self._initialized:
            return

        print("正在初始化OCR模型...")
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'

        model_name = model_name_path

        self._ocr_tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self._ocr_model = AutoModel.from_pretrained(model_name,
                                                    trust_remote_code=True,
                                                    use_safetensors=True)
        self._ocr_model = self._ocr_model.eval().cuda().to(torch.bfloat16)

        self._initialized = True
        print("OCR模型初始化完成")

    def get_ocr_model(self):
        """获取OCR模型和tokenizer"""
        if not self._initialized:
            raise RuntimeError("OCR模型未初始化，请先调用init_ocr_model()")
        return self._ocr_model, self._ocr_tokenizer

    def is_ocr_initialized(self):
        """检查OCR模型是否已初始化"""
        return self._initialized


# 创建全局实例
global_models = GlobalModels()