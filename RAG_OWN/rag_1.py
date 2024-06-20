# from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import Docx2txtLoader
from langchain_chroma import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.memory.buffer import ConversationBufferMemory
from langchain.schema import HumanMessage
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
# import openai
# from llama_index.llms.openai_like import OpenAILike
# from llama_index.core.base.llms.types import ChatMessage,MessageRole
#
# llm = OpenAILike(model="qwen2",api_base="http://192.168.100.111:8000/v1",api_key="dummy")
#
# print(llm.chat(messages=[ChatMessage(role=MessageRole.SYSTEM,content="You are a helpful assistant"),
#                         ChatMessage(role=MessageRole.USER,content="Plz introduce yourself")],max_tokens=100))


# print(str(llm.chat(messages=[
#    {"role":"system","content":"You are a helpful assistant"},
#    {"role":"user","content":"Hello!"}
# ],formatted=True,max_tokens=80,temperature=0.5)))
import os
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:8000/v1/"
os.environ["OPENAI_API_KEY"] = "xxx"

model_name = "thenlper/gte-large"
# embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"
# embeddings = ModelScopeEmbeddings4LlamaIndex(embedding_model)
embeddings = HuggingFaceEmbeddings(model_name=model_name)
# messages = [
#    ("system", "You are a helpful assistant"),
#    ("human", "你好!"),
# ]
# response = llm([HumanMessage(content=prompt.format(text=query))])
llm = ChatOpenAI(model="qwen2", max_tokens=100, max_retries=2)
loader = Docx2txtLoader(
    file_path="WEYON_LLM/dataFiles/湖南科技大学2022届毕业生就业质量年度报告12.31.docx")
data = loader.load()
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

# template = """
# [INST] <>
# 你现在是一名十分精通大学生就业的大学就业处指导老师，使用如下的信息去回答问题
# <>
#
# {context}
#
# {question}
#
# [/INST]
# """
#
# prompt = PromptTemplate(
#   input_variables=["context", "question"], template=template)

custom_template = """
[INST] <>
You are now a college career office instructor who is well versed in career guidance for college students, and I am going to give you a history of a conversation and a question that
You need to rewrite the question so that it is extracted separately, and add: 'Answer in Chinese' at the end of the extracted question.
If you don't know the answer to this question, please reply strictly to the statement I've given: 'Sorry, Private Marseille'.
<>

对话历史:
{chat_history}

提出的问题：{question}

改写的问题：
[/INST]
"""

CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)
# CUSTOM_QUESTION_PROMPT = PromptTemplate(input_variables=['chat_history', 'question'],
# template=custom_template)

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=memory,
    retriever=db.as_retriever(search_kwargs={"k": 2}),
    condense_question_prompt=CUSTOM_QUESTION_PROMPT,
)

#qa_chain = CUSTOM_QUESTION_PROMPT | memory | db.as_retriever(search_kwargs={"k": 2}) | llm


# qa_chain = RetrievalQA.from_chain_type(
#    llm=llm,
#    chain_type="stuff",
#    retriever=db.as_retriever(search_kwargs={"k": 2}),
#    return_source_documents=True,
#    chain_type_kwargs={"prompt": prompt}
# )
#
query = "湖南科技大学2022届毕业生就业质量调研问卷面向了多少名毕业生?"

result_ = qa_chain({"question": query})

result = result_["answer"].strip()

print(result)


# response = llm.invoke(prompt.format(text=query))


# openai.base_url = "http://192.168.100.111:8000/v1"


# def get_completion(prompt):
#    headers = {'Content-Type':'application/json'}
#    data = {"prompt":prompt}
#    response = requests.post(url="http://192.168.100.111:8000/v1/completions",
#                             headers=headers,
#                             data=json.dumps(data))
#    return response.json()['response']

# openai.api_key="xxx"
# completion = openai.chat.completions.create(
#    model="qwen2",
#    messages=[
#        {
#            "role": "user",
#            "content": "How do I output all files in a directory using Python?",
#        },
#    ],
# )
# print(completion.choices[0].message.content)
# completion = openai.completions.create(prompt="你好",model="qwen2")
# print(completion[completion.choices[0].text])
# def get_completion(prompt):
#    headers = {'Content-Type':'application/json'}
#    data = {"prompt":prompt,"model":'qwen2',"temperature":0.5,"max_tokens":100}
#    response = requests.post(url="http://192.168.100.111:8000/v1/completions",
#                             headers=headers,
#                             data=json.dumps(data))
#    return response.json()
#
# if __name__ == '__main__':
#    print(get_completion('你好'))
