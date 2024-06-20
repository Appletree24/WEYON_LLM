from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from utils.ModelScopeEmbeddings4LlamaIndex import ModelScopeEmbeddings4LlamaIndex
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    set_global_handler
)
import os
import phoenix as px
session = px.launch_app()


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

while True:
    query = input("Q:")
    response = query_engine.query(query)
    print(response)
