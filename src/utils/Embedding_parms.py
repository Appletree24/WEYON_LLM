#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Embedding_parms.py
# @Time      :2024/07/19 16:06:24
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 方便获取Embedding模型参数的工具类，为了注册配置Xinference中的模型
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from sentence_transformers import SentenceTransformer


class EmbeddingTool:
    model_name_or_path: str
    model: SentenceTransformer

    def __init__(self, model_name_or_path: str):
        self.model = SentenceTransformer(model_name_or_path=model_name_or_path)

    def get_embedding_dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def get_max_tokens(self) -> int:
        return self.model.tokenizer.model_max_length
