from langchain_core.embeddings.embeddings import Embeddings
from typing import Any, List
from retriever import embedding


@embedding.register
class ModelScopeEmbeddings(Embeddings):
    embed: Any = None
    model_id: str = "iic/nlp_gte_sentence-embedding_chinese-base"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        inputs = {"source_sentence": texts}
        return self.embed(input=inputs)['text_embedding']

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def __init__(self, modelscope_embeddings_model_id: str = model_id) -> None:
        super().__init__(**{})
        try:
            from modelscope.models import Model
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            self.embed = pipeline(Tasks.sentence_embedding, model=self.model_id)

        except ImportError as e:
            raise ValueError(
                "Could not import some python packages." "Please install it with `pip install modelscope`.") from e
