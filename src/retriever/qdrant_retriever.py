from langchain_core.documents import Document
from langchain_core.runnables import ConfigurableField, RunnableSerializable

import retriever
from embedding import modelscope_embedding
from retriever.vector_store import qdrant

_ = modelscope_embedding
_ = qdrant


@retriever.register
def qdrant_retriever(QdrantVectorStore: qdrant.QdrantVectorStore, retriever_config) -> RunnableSerializable[
    str, list[Document]]:
    return (QdrantVectorStore
            .as_retriever(search_type="similarity", search_kwargs={"k": retriever_config['top_k']})
            .configurable_fields(search_kwargs=ConfigurableField(id="search_kwargs_qdrant",
                                                                 name="Search Kwargs",
                                                                 description="The search kwargs to use"
                                                                 )))
