#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :parent_retriever.py
# @Time      :2024/07/10 08:47:13
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Langchain中的父子Retriever
# @Version   :1.0
# @From      :https://x.com/zhanghaili0610/status/1692887244745388125
# 请不要用GPT生成代码中的注释，谢谢。
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import Docx2txtLoader
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

template = """
请根据下面给出的上下文回答问题:
{context}

问题:{question}
"""

prompt = ChatPromptTemplate.from_template(template)

embedding_name = "BAAI/bge-m3"

embeddings = HuggingFaceEmbeddings(model_name=embedding_name)


llm = ChatOpenAI(model="qwen2-pro", max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)


loaders = [
    Docx2txtLoader(file_path='WEYON_LLM/RAG/HNUST.docx'),
    Docx2txtLoader(file_path='WEYON_LLM/RAG/Mao.docx'),
]

docs = []

for loader in loaders:
    docs.extend(loader.load())

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

vectorstore = Chroma(
    collection_name="split_parents", embedding_function=embeddings
)

store = InMemoryStore()

retriever = ParentDocumentRetriever(
    parent_splitter=parent_splitter,
    child_splitter=child_spillter,
    vectorstore=vectorstore,
    docstore=store,
)

retriever.add_documents(docs)

response = retriever.get_relevant_documents("湖南科技大学现在有教职工多少人?专任教师多少？有没有'四个一批'人才")

print(response)

qa_chain = RunnableMap({
    "context": lambda x: retriever.get_relevant_documents(x["question"]),
    "question": lambda x: x["question"]
}) | prompt | llm | StrOutputParser()

response = qa_chain.invoke({"question": "毕业生省内就业行业主要为?"})
print(response)
