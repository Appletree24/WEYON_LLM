#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :rag.py
# @Time      :2024/07/10 11:04:46
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Advanced RAG汇总，距离完全体还有很长一段距离
# @Modules   :
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain_community.document_loaders import Docx2txtLoader
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import ParentDocumentRetriever
from langchain.schema.runnable import RunnableMap
from langchain.schema.output_parser import StrOutputParser
# from qdrant_client.http.exceptions import UnexpectedResponse as NOTFOUND_COLLECTION
from langchain_community.document_transformers.long_context_reorder import LongContextReorder
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain_community.document_transformers import EmbeddingsClusteringFilter
from langchain_community.document_transformers.embeddings_redundant_filter import EmbeddingsClusteringFilter
from src.embedding.modelscope_embedding import ModelScopeEmbeddings
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import ParentDocumentRetriever
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers import MergerRetriever

# ATTENTION 如果按照之前的策略，一个用户给一个Collection，那Collection中的Points数量会不断增加，如何解决？
# 并且如果一个Collection里放很多文档，有没有必要做Merger了？那不一个Retriever就解决了？
# SOLVE 目前的解决方案是一个Retriever，但是绝对是不可靠的，需要进一步解决

template = """
你是一名很有用的小助手，请根据下面给出的上下文回答问题:
{context}

问题：{question}

"""

prompt = ChatPromptTemplate.from_template(template)

embeddings_hf = HuggingFaceEmbeddings(model_name="thenlper/gte-large")
embeddings_bge = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
embeddings_jina = HuggingFaceEmbeddings(
    model_name="jinaai/jina-embeddings-v2-base-zh")
embeddings_iic = ModelScopeEmbeddings(
    modelscope_embeddings_model_id="iic/nlp_gte_sentence-embedding_chinese-base")

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",
    "\uff0c",
    "\u3001",
    "\uff0e",
    "\u3002",
    "",
])

child_spillter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",
    "\uff0c",
    "\u3001",
    "\uff0e",
    "\u3002",
    "",
])

llm = ChatOpenAI(model="qwen2-pro", max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)


loaders = [
    Docx2txtLoader(
        file_path='/home/kemove/AI_Projects/zzh/WEYON_LLM/RAG/HNUST.docx'),
    Docx2txtLoader(file_path='WEYON_LLM/RAG/Mao.docx'),
    Docx2txtLoader(
        file_path='WEYON_LLM/RAG/HengYang.docx'),
    Docx2txtLoader(file_path='WEYON_LLM/RAG/Chuanmei.docx'),
    Docx2txtLoader(file_path='WEYON_LLM/RAG/Jingmao.docx'),
]

docs = []

for loader in loaders:
    docs.extend(loader.load())


qdrant_client = QdrantClient(location="192.168.100.111:6333")

if qdrant_client.collection_exists(collection_name="rag_test_child_dim_1024") is False:
    qdrant_client.create_collection(
        collection_name="rag_test_child_dim_1024",
        vectors_config=models.VectorParams(
            size=1024,
            distance=models.Distance.COSINE
        )
    )

collection_status = qdrant_client.get_collection(
    collection_name="rag_test_child_dim_1024")

if collection_status.status == 'green':
    print("Collection is Ready")
elif collection_status.status == 'red':
    print("An error occurred which the engine could not recover from")

# TODO 经测试发现，Qdrant不会检测Collection中的Points是否重复，所以如果按当前测试逻辑，Points数会翻番
# SOLVE 1.检测文件名重复与否，来判断此次是否进行切块（问题在于文件名如何保证唯一？MD5？好处是同时优化了chunk处理时间与数据库points重复叠加）

parent_store = InMemoryStore()
qdrant_child = Qdrant(
    qdrant_client,
    collection_name="rag_test_child_dim_1024",
    embeddings=embeddings_bge
)

retriever = ParentDocumentRetriever(
    parent_splitter=parent_splitter,
    child_splitter=child_spillter,
    vectorstore=qdrant_child,
    docstore=parent_store,
)

# collection_counts = qdrant_client.count(
#    collection_name="rag_test_child_dim_1024",
#    exact=True
# )

# NOTE 来解释一下add_documents这个函数
# add_documents里有一个uuid64的算法，每次都随机生成一批新的keys放在父亲文档中，如果父亲要用内存式的存储，就导致每次都生成了新的key，如果第二次不执行这个函数了，那当然就找不到结果，因为方法拿到的key和第一次不一样了

# retriever.add_documents(docs)
retriever.add_documents(docs)

print(retriever.get_relevant_documents("湖南科技大学现在有教职工多少人?专任教师多少？有没有'四个一批'人才"))


redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings_jina)

relevant_filter = EmbeddingsFilter(embeddings=embeddings_jina, k=5)

reorder = LongContextReorder()

compressor = LLMChainExtractor.from_llm(llm)


pipeline = DocumentCompressorPipeline(
    transformers=[compressor, redundant_filter, relevant_filter, reorder]
)

compression_retriever_reordered = ContextualCompressionRetriever(
    base_retriever=retriever,
    base_compressor=pipeline,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=compression_retriever_reordered
)

print(qa_chain.invoke({"query": "湖南科技大学现在有教职工多少人?专任教师多少？有没有'四个一批'人才"}))


# qa_chain = RunnableMap(
#    {
#        "context": lambda x: compression_retriever_reordered.get_relevant_documents(x["question"]),
#        "question": lambda x: x["question"]
#    }
# ) | prompt | llm | StrOutputParser()
#
# response = qa_chain.invoke(
#    {"question": "湖南科技大学的校党委书记是谁?"}
# )
#
# print(response)

# try:
#    qdrant_client.get_collection(collection_name="rag_test_child_dim_1024")
# except NOTFOUND_COLLECTION:
#    qdrant_client.create_collection(
#        collection_name="rag_test_child_dim_1024",
#        vectors_config=models.VectorParams(
#            size=1024,
#            distance=models.Distance.COSINE
#        )
#    )


# for loader in loaders:
#    cur_docs = loader.load()
#    Qdrant.from_documents(
#        child_spillter.split_documents(cur_docs),
#        embeddings_bge,
#        location="http://192.168.100.111:6333",
#        collection_name="rag_test_child_dim_1024"
#    )
