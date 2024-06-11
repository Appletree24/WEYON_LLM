from llama_index.core.embeddings import BaseEmbedding
from typing import Any, List

class ModelScopeEmbeddings4LlamaIndex(BaseEmbedding):
    # 定义类属性，embed 用于存储嵌入模型的实例，model_id 用于存储模型标识符
    embed: Any = None
    model_id: str = "iic/nlp_gte_sentence-embedding_chinese-base"

    def __init__(self, model_id: str, **kwargs: Any) -> None:
        # 调用父类的构造函数，并传递其他参数
        super().__init__(**kwargs)
        try:
            # 尝试导入必要的 ModelScope 模块
            from modelscope.models import Model
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            # 使用 ModelScope 的 pipeline 函数初始化嵌入模型
            self.embed = pipeline(Tasks.sentence_embedding, model=self.model_id)
        except ImportError as e:
            # 如果导入失败，抛出 ValueError 并提供错误信息
            raise ValueError("Could not import some python packages.") from e

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
