#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Evaluating_Llama.py
# @Time      :2024/07/22 11:38:48
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 借助llamaindex实现的评测模块，因为评测需要同步调用多次大模型，所以就涉及到async，但Jupyter Notebook会自己起一个线程，就导致里面的代码无法正常运行，可以使用nest_asyncio.apply()解决
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_community.embeddings import XinferenceEmbeddings
from llama_index.core.evaluation import FaithfulnessEvaluator
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import VectorStoreIndex
import logging
import sys
import os

os.environ["http_proxy"] = "http://192.168.100.111:7890"
os.environ["https_proxy"] = "http://192.168.100.111:7890"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)


xinference_embeddings = LangchainEmbedding(XinferenceEmbeddings(
    server_url="http://192.168.100.111:9997",
    model_uid="xiaobu-v2"
))

llm = OpenAILike(model="qwen2-pro", api_base="http://192.168.100.111:8001/v1",
                 api_key="tree", max_tokens=1000)

Settings.llm = llm
Settings.embed_model = xinference_embeddings

documents = SimpleDirectoryReader(
    '/home/kemove/AI_Projects/zzh/WEYON_LLM/resources/data/journey').load_data()

index = VectorStoreIndex.from_documents(documents=documents)

evaluator = FaithfulnessEvaluator(llm=llm)

query_engine = index.as_query_engine()

response = query_engine.query("在这段故事中，谁的孩子被摔死了?")

eval_result = evaluator.evaluate_response(
    response=response)

print(str(eval_result.passing))
