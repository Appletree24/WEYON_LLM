#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :phoenix_log.py
# @Time      :2024/07/03 15:32:40
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: LangSmith的替代品，无法平替，下选
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from src.embedding.modelscope_embedding import ModelScopeEmbeddings
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader
)
import phoenix as px

# 启动 Phoenix 应用
session = px.launch_app()

# 设置 OpenTelemetry 的endpoint，用于发送追踪数据
endpoint = "http://127.0.0.1:9997/v1/traces"

# 数据文件目录
DATA_DIRECTORY = "WEYON_LLM/dataFiles"

# 设置追踪提供者和追踪限制
tracer_provider = TracerProvider(
    span_limits=SpanLimits(max_attributes=100_000))  # 设置追踪的最大属性数量
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint)))  # 添加简单的追踪处理器，将追踪数据导出到指定的终端点

# 初始化 LlamaIndex 的追踪工具
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

# 设置嵌入模型的 ID
embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"
# 实例化嵌入模型
embeddings = ModelScopeEmbeddings(model_id=embedding_model)

# NOTICE: max_tokens不宜过大，建议在300以下，过大会导致负数传参
Settings.llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:9997/v1",
                          api_key="dummy", max_tokens=1000)
Settings.embed_model = embeddings  # 设置嵌入模型

# 从数据目录加载文档
documents = SimpleDirectoryReader(DATA_DIRECTORY).load_data(show_progress=True)
# 从文档创建向量存储索引
index = VectorStoreIndex.from_documents(documents)

# 从索引中创建查询引擎
query_engine = index.as_query_engine()

# 处理用户输入的查询,防止session关闭
try:
    while True:
        query = input("Q:")  # 接收用户输入的查询
        query_engine.query(query)  # 使用查询引擎查询输入内容
except KeyboardInterrupt:
    print("Session closed")
