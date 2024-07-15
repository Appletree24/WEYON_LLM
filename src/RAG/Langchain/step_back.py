#!//home/kemove/miniconda3/envs/llm/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :step_back.py
# @Time      :2024/07/15 09:00:31
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: RAG中的Step-Back模块
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

# ATTENTION Langchain的模块很恶心，这个代码需要降级pydantic为1.10.3才能正常运行

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True, temperature=0)

loader = Docx2txtLoader(file_path='WEYON_LLM/resources/doc/Chuanmei.docx')
doc_file = loader.load()

parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1024, chunk_overlap=50)

split_docs = parent_splitter.split_documents(doc_file)

examples = [
    {
        "input": "Could the members of The Police perform lawful arrests?",
        "output": "what can the members of The Police do?",
    },
    {
        "input": "Jan Sindel’s was born in what country?",
        "output": "what is Jan Sindel’s personal history?",
    },
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", '{input}'),
        ("ai", '{output}'),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
            You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is easier to answer. Here are a few examples:
         """),
        few_shot_prompt,
        ("human", "{question}")
    ]
)

generate_queries_step_back = prompt | llm | StrOutputParser()

question = "What is task decomposition for LLM agents?"

response_prompt_template = """
You are an expert of world knowledge. I am going to ask you a question. Your response should be comprehensive and not contradicted with the following context if they are relevant. Otherwise, ignore them if they are not relevant.

{normal_context}
{step_back_context}

Original Question: {question}
Answer:
"""
response_prompt = ChatPromptTemplate.from_template(response_prompt_template)

vectorstore = Chroma.from_documents(
    split_docs, embedding=HuggingFaceEmbeddings(model_name="nomic-ai/nomic-embed-text-v1.5"))

retriever = vectorstore.as_retriever()

chain = (
    {
        # Retrieve context using the normal question
        "normal_context": RunnableLambda(lambda x: x["question"]) | retriever,
        # Retrieve context using the step-back question
        "step_back_context": generate_queries_step_back | retriever,
        # Pass on the question
        "question": lambda x: x["question"],
    }
    | response_prompt
    | ChatOpenAI(temperature=0)
    | StrOutputParser()
)

chain.invoke({"question": question})
