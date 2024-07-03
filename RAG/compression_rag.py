#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :compression_rag.py
# @Time      :2024/07/03 15:46:02
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 压缩RAG
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain.prompts import PromptTemplate
template = """
<user>:
Context:{context}

Question:{question}

Use the above Context to answer the user's question.Consider only the Context provided above to formulate response.If the Question asked does not match with the Context provided just say 'I do not know thw answer'.
<assistant>:

"""
prompt = PromptTemplate(
    input_variables=["context", "question"], template=template)
chain_type_kwargs = {"prompt": prompt}
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:9997/v1/"
os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

model_name = "thenlper/gte-large"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

loader = PyPDFLoader("WEYON_LLM/dataFiles/1910.02054v3.pdf")

pdf_docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700, chunk_overlap=70)

split_documents = text_splitter.split_documents(pdf_docs)

llm = ChatOpenAI(model="Qwen2-Local", max_tokens=200, max_retries=2)


def pretty_print_docs(docs):
    print(f"\n{'-'* 100}\n".join([F"Document{i+1}:\n\n" +
          d.page_content for i, d in enumerate(docs)]))


vector_store = Chroma.from_documents(split_documents, embeddings, persist_directory="db",
                                     collection_metadata={"hnsw:space": "cosine"})

retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 编写Pipeline embeddings + EmbeddingsRedundantFilter + EmbeddingsFilter
# NOTE：EmbeddingsRedundantFilter是为了去除冗余的文本，因为在文档中可能会有类似的文本
# NOTE: EmbeddingsFilter是为了是为了提取与提问问题有足够相似度的文本
redundan_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
relevant_filter = EmbeddingsFilter(embeddings=embeddings, k=5)

# pipeline_compressor = DocumentCompressorPipeline(
#    transformers=[redundan_filter, relevant_filter])
# compression_retriever_pipeline = ContextualCompressionRetriever(
#    base_retriever=retriever, base_compressor=pipeline_compressor)
# compressed_docs = compression_retriever_pipeline.get_relevant_documents(
#   "What is ZeRO?")
# pretty_print_docs(compressed_docs)


# 结合compressor, LLMChainExtractor将只返回与文档相关的内容
compressor = LLMChainExtractor.from_llm(llm)

new_pipeline = DocumentCompressorPipeline(
    transformers=[compressor, redundan_filter, relevant_filter])

new_compression_retriever = ContextualCompressionRetriever(base_retriever=retriever,
                                                           base_compressor=new_pipeline)

qa = RetrievalQA.from_chain_type(llm=llm,
                                 chain_type="stuff",
                                 chain_type_kwargs=chain_type_kwargs,
                                 return_source_documents=True,
                                 verbose=True,
                                 retriever=new_compression_retriever)
response = qa("What's the ZeRO-3, if you know it, plz introduce it in detail")
print(response['result'].split("<|endoftext|>")[0])



# relevant_docs = retriever.get_relevant_documents(
#    query="What is ZeRO-3 stage?")


# compression_retriever = ContextualCompressionRetriever(base_retriever=retriever,
#                                                       base_compressor=compressor)

# embeddings_filter = EmbeddingsFilter(embeddings=embeddings)
# compression_retriever_filter = ContextualCompressionRetriever(base_retriever=retriever,
#                                                              base_compressor=embeddings_filter)
#
# compressed_docs = compression_retriever_filter.get_relevant_documents(
#    query="What is ZeRO-3 stage?")
#
# qa = RetrievalQA.from_chain_type(llm=llm,
#                                 chain_type="stuff",
#                                 retriever=compression_retriever_filter,
#                                 verbose=True)
#
