from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.messages import HumanMessage
import os

# 配OpenAI接口的系统变量
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:8000/v1/"
os.environ["OPENAI_API_KEY"] = "xxx"

# 从Huggingface下embedding
model_name = "thenlper/gte-large"
# 也可以用我写的ModelScope4Embedding类从ModelScope下载
embeddings = HuggingFaceEmbeddings(model_name=model_name)
# 接口参数与OpenAI保持一致 看官网文档即可
llm = ChatOpenAI(model="qwen2", max_tokens=100, max_retries=2)
# Langchain官网有几个读Doc的类，这里用Docx2txtLoader
loader = Docx2txtLoader(
    file_path="WEYON_LLM/dataFiles/湖南科技大学2022届毕业生就业质量年度报告12.31.docx")
data = loader.load()
# 对中文separator做特殊处理
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",  # Zero-width space
    "\uff0c",  # Fullwidth comma
    "\u3001",  # Ideographic comma
    "\uff0e",  # Fullwidth full stop
    "\u3002",  # Ideographic full stop
    "",
])
doc_chunks = text_splitter.split_documents(data)
db = Chroma.from_documents(doc_chunks, embeddings, persist_directory="db")

# 问题重述
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

# 问题重述模板
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# 历史感知检索器
history_aware_retriever = create_history_aware_retriever(
    llm, db.as_retriever(search_kwargs={"k": 2}), contextualize_q_prompt
)

# 问题回答System模板
qa_system_prompt = """
你是一名大学就业处指导老师，使用如下的信息去回答问题，\
如果你不知道准确的答案，请说“私密马赛，我不知道”。\
最多使用五句话来回答，并且保持回答的准确性。\

{context}
"""

# 问题回答模板
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)


# 创建问题回答链
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever, question_answer_chain)

# 详细看invoke的源码，这里的chat_history是一个列表
chat_history = []

query = "湖南科技大学2022届毕业生初次毕业去向落实率为84.58%，其中灵活就业率仅为9.14%。评价一下2022年的湖南科技大学毕业生质量高低水平"

ai_msg_1 = rag_chain.invoke({"input": query, "chat_history": chat_history})

# ATTENTION Langchain建议用HumanMessage类来包装问题
chat_history.extend([HumanMessage(content=query), ai_msg_1["answer"]])
print(ai_msg_1["answer"])

second_question = "湖南科技大学2022届本科毕业生的灵活就业率是多少？"

ai_msg_2 = rag_chain.invoke(
    {"input": second_question, "chat_history": chat_history})

print(ai_msg_2["answer"])
