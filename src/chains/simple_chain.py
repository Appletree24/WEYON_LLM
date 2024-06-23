from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import chains
from llm import chat_openai
from retriever import qdrant_retriever

_ = chat_openai
_ = qdrant_retriever


@chains.register
def simple_chain(ServeChatModel, qdrant_retriever):
    message = """
    Answer this question using the provided context. 
    {question}
    Context:
    {context}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("human", message)
    ])
    return {"context": qdrant_retriever, "question": RunnablePassthrough()} | prompt | ServeChatModel
