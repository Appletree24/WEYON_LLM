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
from retriever import embedding


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
                Tasks.sentence_embedding, model=self.model_id)

        except ImportError as e:
            raise ValueError(
                "Could not import some python packages." "Please install it with `pip install modelscope`.") from e
