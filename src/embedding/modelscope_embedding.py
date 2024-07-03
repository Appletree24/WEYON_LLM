#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :modelscope_embedding.py
# @Time      :2024/07/03 15:41:28
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 从ModelScope上下载embedding,为了兼容Langchain
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain_core.embeddings.embeddings import Embeddings
from typing import Any, List
import embedding


@embedding.register
class ModelScopeEmbeddings(Embeddings):
    embed: Any = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        inputs = {"source_sentence": texts}
        return self.embed(input=inputs)['text_embedding']

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def __init__(self, modelscope_embeddings_model_id: str) -> None:
        super().__init__(**{})
        try:
            from modelscope.models import Model
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            self.embed = pipeline(
                Tasks.sentence_embedding, model=modelscope_embeddings_model_id)

        except ImportError as e:
            raise ValueError(
                "Could not import some python packages." "Please install it with `pip install modelscope`.") from e

    def _get_query_embedding(self, query: str) -> List[float]:
        # 将查询中的换行符替换为空格
        text = query.replace("\n", " ")
        # 准备输入格式
        inputs = {"source_sentence": [text]}
        # 获取嵌入向量并返回第一个结果的嵌入向量
        return self.embed(input=inputs)['text_embedding'][0].tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        # 将文本中的换行符替换为空格
        text = text.replace("\n", " ")
        # 准备输入格式
        inputs = {"source_sentence": [text]}
        # 获取嵌入向量并返回第一个结果的嵌入向量
        return self.embed(input=inputs)['text_embedding'][0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 将每个文本中的换行符替换为空格
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        # 准备输入格式
        inputs = {"source_sentence": texts}
        # 获取所有文本的嵌入向量并返回
        return self.embed(input=inputs)['text_embedding'].tolist()

    async def _aget_query_embedding(self, query: str) -> List[float]:
        # 异步方法获取查询的嵌入向量，调用同步版本
        return self._get_query_embedding(query)
