#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :HyDE.py
# @Time      :2024/07/15 10:27:02
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description:HyDE模块
# @Version   :1.0
# @From      : https://arxiv.org/abs/2212.10496
# @Conda Env : rag_zzh
# 请不要用GPT生成代码中的注释，谢谢。
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True, temperature=0)

template = """
请写一段科学论文来回答问题
问题 {question}
论文：
"""
loader = PyPDFLoader(file_path="WEYON_LLM/resources/LIM.pdf")

pdf_file = loader.load()

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1024, chunk_overlap=50)

split_docs = splitter.split_documents(pdf_file)

vectorstore = Chroma.from_documents(
    split_docs, embedding=HuggingFaceEmbeddings(model_name="BAAI/bge-m3"))

retriever = vectorstore.as_retriever()

prompt_hyde = ChatPromptTemplate.from_template(template)

generate_docs_for_retrieval = (
    prompt_hyde | llm | StrOutputParser()
)

question = "What is LIM phenomenon?"
retrieval_chain = generate_docs_for_retrieval | retriever

retrieved_docs = retrieval_chain.invoke({"question": question})

template = """Answer the following question based on this context:

{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

final_rag_chain = (
    prompt
    | llm
    | StrOutputParser()
)

print(final_rag_chain.invoke({"context": retrieved_docs, "question": question}))
