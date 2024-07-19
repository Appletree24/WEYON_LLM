from typing import Dict

from langchain_qdrant import Qdrant
from retriever import vector_store

# from embedding import modelscope_embedding

from langchain_community.embeddings import XinferenceEmbeddings

# _ = modelscope_embedding


@vector_store.register
def qdrant_client(qdrant_config):
    from qdrant_client import QdrantClient
    return QdrantClient(**qdrant_config)


@vector_store.register
class QdrantVectorStore(Qdrant):
    """Qdrant VectorStore."""

    def __init__(self, qdrant_client, xinference_embedding_config, qdrant_vectorstore_config: Dict):
        client = qdrant_client
        collection = 'qdrant_default'
        embed = XinferenceEmbeddings(**xinference_embedding_config)
        if qdrant_vectorstore_config:
            collection = qdrant_vectorstore_config.get(
                'collection_name', 'qdrant_default')
        super().__init__(client=client, collection_name=collection, embeddings=embed)
