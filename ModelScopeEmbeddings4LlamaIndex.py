from llama_index.core.embeddings import BaseEmbedding
from typing import Any, List


class ModelScopeEmbeddings4LlamaIndex(BaseEmbedding):
    embed: Any = None
    model_id: str = "iic/nlp_gte_sentence-embedding_chinese-base"

    def __init__(
            self,
            model_id: str,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        try:
            from modelscope.models import Model
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            self.embed = pipeline(
                Tasks.sentence_embedding, model=self.model_id)
        except ImportError as e:
            raise ValueError(
                "Could not import some python packages."
            ) from e

    def _get_query_embedding(self, query: str) -> List[float]:
        text = query.replace("\n", " ")
        inputs = {"source_sentence": [text]}
        return self.embed(input=inputs)['text_embedding'][0].tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        inputs = {"source_sentence": [text]}
        return self.embed(input=inputs)['text_embedding'][0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        inputs = {"source_sentence": texts}
        return self.embed(input=inputs)['text_embedding'].tolist()

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)
