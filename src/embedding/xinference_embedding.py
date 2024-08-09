from langchain_community.embeddings import XinferenceEmbeddings

import embedding


@embedding.register
def xinference_embedding(xinference_embedding_config):
    return XinferenceEmbeddings(**xinference_embedding_config)
