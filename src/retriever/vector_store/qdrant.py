from typing import Dict

from langchain_qdrant import Qdrant

from embedding import xinference_embedding
from retriever import vector_store


@vector_store.register
def qdrant_client(qdrant_config):
    from qdrant_client import QdrantClient
    return QdrantClient(**qdrant_config)


@vector_store.register
class QdrantVectorStore(Qdrant):
    """Qdrant VectorStore."""

    def __init__(self, qdrant_client, xinference_embedding: xinference_embedding.XinferenceEmbeddings,
                 qdrant_vectorstore_config: Dict):
        client = qdrant_client
        collection = 'qdrant_default'
        embed = xinference_embedding
        if qdrant_vectorstore_config:
            collection = qdrant_vectorstore_config.get(
                'collection_name', 'qdrant_default')
        super().__init__(client=client, collection_name=collection, embeddings=embed)
