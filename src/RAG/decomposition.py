#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :decomposition.py
# @Time      :2024/07/14 11:02:36
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description:Multi Query中的Decomposition模块
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader
from langchain import hub
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.text_splitter import RecursiveCharacterTextSplitter
from operator import itemgetter


loader = Docx2txtLoader(file_path='WEYON_LLM/resources/doc/Chuanmei.docx')
doc_file = loader.load()

parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1024, chunk_overlap=50)

split_docs = parent_splitter.split_documents(doc_file)

template = """
您是一个有用的助手，可以生成与输入问题相关的多个子问题。

目标是将输入问题分解成一组可以单独回答的子问题。

生成与以下内容相关的多个搜索查询问题

输出（3 个查询）：
"""

prompt_decomposition = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True, temperature=0)

generate_queries_decomposition = (
    prompt_decomposition | llm | StrOutputParser() | (lambda x: x.split("\n"))
)

questions = generate_queries_decomposition.invoke({"question": "如何学习数学?"})

template = """
这是你需要回答的问题

\n - - \n {question} \n --- \n

这里是任何可用的背景问题 + 答案对：

\n --- \n {q_a_pairs} \n --- \n

这里是与问题相关的额外背景： 

\n --- \n {context} \n --- \n

使用上述上下文和任何背景问题 + 答案对来回答问题： \n {question}
"""

decomposition_prompt = ChatPromptTemplate.from_template(template)


def format_qa_pair(question, answer):
    """Format Q and A pair"""

    formatted_string = ""
    formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
    return formatted_string.strip()


qa_pairs = ""

vectorstore = Chroma.from_documents(
    split_docs, embedding=HuggingFaceEmbeddings(model_name="nomic-ai/nomic-embed-text-v1.5"))

retriever = vectorstore.as_retriever()

for q in questions:
    rag_chain = (
        {"context": itemgetter("question") | retriever,
         "question": itemgetter("question"),
         "qa_pairs": itemgetter("qa_pairs")}
        | decomposition_prompt
        | llm
        | StrOutputParser()
    )

    answer = rag_chain.invoke({"question": q, "qa_pairs": qa_pairs})
    qa_pairs = format_qa_pair(q, answer)
    qa_pairs = qa_pairs + "\n---\n" + qa_pairs

# Answer Individually
prompt_rag = hub.pull("rlm/rag-prompt")


def retrieve_and_rag(question, prompt_rag, sub_question_generator_chain):
    """RAG on each sub-question"""

    # Use our decomposition /
    sub_questions = sub_question_generator_chain.invoke({"question": question})

    # Initialize a list to hold RAG chain results
    rag_results = []

    for sub_question in sub_questions:

        # Retrieve documents for each sub-question
        retrieved_docs = retriever.get_relevant_documents(sub_question)

        # Use retrieved documents and sub-question in RAG chain
        answer = (prompt_rag | llm | StrOutputParser()).invoke({"context": retrieved_docs,
                                                                "question": sub_question})
        rag_results.append(answer)

    return rag_results, sub_questions


answers, questions = retrieve_and_rag(
    "如何学习数学?", prompt_rag, generate_queries_decomposition)


def format_qa_pairs(questions, answers):
    """Format Q and A pairs"""

    formatted_string = ""
    for i, (question, answer) in enumerate(zip(questions, answers), start=1):
        formatted_string += f"Question {i}: {question}\nAnswer {i}: {answer}\n\n"
    return formatted_string.strip()


context = format_qa_pairs(questions, answers)

template = """
下面是一组 Q+A 对：

{context}

利用这些内容综合回答问题： {question}
"""

prompt = ChatPromptTemplate.from_template(template)

final_rag_chain = (
    prompt
    | llm
    | StrOutputParser()
)

print(final_rag_chain.invoke({"question": "如何学习数学", "context": context}))
