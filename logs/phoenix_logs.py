import phoenix as px
session = px.launch_app()
import os
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    set_global_handler
)
from llama_index.llms.openai_like import OpenAILike
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if project_root not in sys.path:
    sys.path.append(project_root)

# 下面这句不要动位置
from utils.ModelScopeEmbeddings4LlamaIndex import ModelScopeEmbeddings4LlamaIndex

from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

endpoint = "http://127.0.0.1:6006/v1/traces"
DATA_DIRECTORY = "WEYON_LLM/dataFiles"
tracer_provider = TracerProvider(
    span_limits=SpanLimits(max_attributes=100_000))
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint)))
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"
embeddings = ModelScopeEmbeddings4LlamaIndex(model_id=embedding_model)

Settings.llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:8000/v1",
                          api_key="dummy", max_tokens=1000)
Settings.embed_model = embeddings

documents = SimpleDirectoryReader(DATA_DIRECTORY).load_data(show_progress=True)
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

#query_engine.query("文章主要讲了什么内容?")

while True:
    query = input("Q:")
    response = query_engine.query(query)
    print(response)
