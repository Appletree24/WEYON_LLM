import retriever

from embedding import modelscope_embedding
from retriever.vector_store import qdrant
from langchain_core.vectorstores import VectorStoreRetriever

_ = modelscope_embedding
_ = qdrant


@retriever.register
def qdrant_retriever(QdrantVectorStore) -> VectorStoreRetriever:
    return QdrantVectorStore.as_retriever(search_type="similarity", search_kwargs={"k": 1})
