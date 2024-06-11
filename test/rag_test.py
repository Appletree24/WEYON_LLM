import torch
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import (
    VectorStoreIndex,
    download_loader,
    PromptHelper,
    StorageContext,
    SimpleDirectoryReader,
    ServiceContext,
    set_global_service_context
)

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if project_root not in sys.path:
    sys.path.append(project_root)

from utils.ModelScopeEmbeddings4LlamaIndex import ModelScopeEmbeddings4LlamaIndex
from llama_index.core.node_parser import SimpleNodeParser

embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"

# 使用SimpleDirectoryReader读取指定目录中的数据文件
documents = SimpleDirectoryReader(input_dir="index_project/dataFiles").load_data(show_progress=True)

# 创建一个节点解析器，用于将文档解析为节点，设置chunk_size为1024
node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)

# 从文档中获取节点
base_nodes = node_parser.get_nodes_from_documents(documents=documents)

# 使用指定的模型创建嵌入对象
embeddings = ModelScopeEmbeddings4LlamaIndex(model_id=embedding_model)

# 创建一个类似OpenAI的语言模型对象，指定模型和API信息
llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:8000/v1", api_key="dummy", max_tokens=100)

# 创建服务上下文对象，使用默认配置，嵌入模型和语言模型
service_context = ServiceContext.from_defaults(embed_model=embeddings, llm=llm)

# 设置全局服务上下文，使其在整个应用中可用
set_global_service_context(service_context)

# 从文档创建向量存储索引
index = VectorStoreIndex.from_documents(documents)

# 将索引作为查询引擎
query_engine = index.as_query_engine()

# 使用查询引擎查询问题并获取响应
response = query_engine.query("湖南科技大学毕业生总人数是多少?")

# 打印响应结果
print(response)
