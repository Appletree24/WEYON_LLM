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
from typing import Any
import os


class HistoryChatRAG():

    # 从Huggingface下embedding,指定模型名字
    model_name = ""
    embedding_model = None
    llm = None
    # 详细看invoke的源码，这里的chat_history是一个列表
    chat_history = []
    # 问题重述
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""

    qa_system_prompt = ""

    def __init__(self, model_name: str, openai_api_key: str, openai_api_base: str, qa_system_prompt: str, **kwargs: Any) -> None:
        # 配OpenAI接口的系统变量
        os.environ["OPENAI_API_BASE"] = openai_api_base
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.model_name = model_name
        # 接口参数与OpenAI保持一致 看官网文档即可
        self.llm = ChatOpenAI(model="qwen2", max_tokens=100, max_retries=2)
        self.qa_system_prompt = qa_system_prompt
        try:
            # 也可以用我写的ModelScope4Embedding类从ModelScope下载
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name)
            print("embedding模型加载完成")
        except ImportError as e:
            raise ImportError(
                "Huggingface embedding model not found. Use `pip install langchain_community_huggingface`") from e

    def load_file_and_chunk(self, docx_path: str, chunk_size: int, chunk_overlap: int, persist_directory: str):
        # Langchain官网有几个读Doc的类，这里用Docx2txtLoader
        self.loader = Docx2txtLoader(
            file_path=docx_path)
        data = self.loader.load()
        # 对中文separator做特殊处理
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=[
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
        doc_chunks = self.text_splitter.split_documents(data)
        self.db = Chroma.from_documents(
            doc_chunks, self.embedding_model, persist_directory=persist_directory)

    def completion(self, search_kwargs: int, prompt: str) -> str:
        # 问题重述模板
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        # 历史感知检索器
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.db.as_retriever(
                search_kwargs={"k": search_kwargs}), contextualize_q_prompt
        )
        # 问题回答模板
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )
        # 创建问题回答链
        self.question_answer_chain = create_stuff_documents_chain(
            self.llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(
            self.history_aware_retriever, self.question_answer_chain)

        self.ai_msg = self.rag_chain.invoke(
            {"input": prompt, "chat_history": self.chat_history})
        self.chat_history.extend(
            [HumanMessage(content=prompt), self.ai_msg["answer"]])
        return self.ai_msg["answer"]
