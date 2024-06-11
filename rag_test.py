# 导入必要的模块和类
from llama_index.core.node_parser import SimpleNodeParser
from ModelScopeEmbeddings4LlamaIndex import ModelScopeEmbeddings4LlamaIndex
from llama_index.core import (
    VectorStoreIndex,
    download_loader,
    PromptHelper,
    StorageContext,
    SimpleDirectoryReader,
    ServiceContext,
    set_global_service_context
)
from llama_index.llms.openai_like import OpenAILike
# from llama_index.core.base.llms.types import ChatMessage,MessageRole

import torch

# 定义嵌入模型的标识符
embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"

# 使用 SimpleDirectoryReader 加载文档数据
documents = SimpleDirectoryReader(
    input_dir="rag/dataFiles").load_data(show_progress=True)

# 使用 SimpleNodeParser 解析文档，将文档切分成节点
node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)
base_nodes = node_parser.get_nodes_from_documents(documents=documents)

# 初始化嵌入模型
embeddings = ModelScopeEmbeddings4LlamaIndex(model_id=embedding_model)

# 初始化类 OpenAI 的语言模型，提供模型标识符、API 基础地址和 API 密钥
llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:8000/v1",
                 api_key="dummy", max_tokens=100)

# 创建服务上下文，将嵌入模型和语言模型包含在内
service_context = ServiceContext.from_defaults(embed_model=embeddings, llm=llm)
# 设置全局服务上下文
set_global_service_context(service_context)

# 使用文档创建向量存储索引
index = VectorStoreIndex.from_documents(documents)

# 将索引转换为查询引擎
query_engine = index.as_query_engine()

# 使用查询引擎进行查询
response = query_engine.query("湖南科技大学毕业生总人数是多少?")

# 打印查询结果
print(response)
