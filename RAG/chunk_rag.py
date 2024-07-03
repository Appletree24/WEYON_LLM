#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :rag_3.py
# @Time      :2024/07/03 15:46:19
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: chunk rag
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.readers.file import PDFReader
from llama_index.core import Document, set_global_service_context
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import IndexNode
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
from src.embedding.modelscope_embedding import ModelScopeEmbeddings

embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"
sub_chunk_sizes = [128, 256, 512]

loader = PDFReader()
docs_0 = loader.load_data(file=Path("WEYON_LLM/dataFiles/llama2.pdf"))
doc_text = "\n\n".join([d.get_content() for d in docs_0])
docs = [Document(text=doc_text)]

node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)
base_nodes = node_parser.get_nodes_from_documents(documents=docs)
embeddings = ModelScopeEmbeddings(model_id=embedding_model)

llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:9997/v1",
                 api_key="dummy", max_tokens=100)

service_context = ServiceContext.from_defaults(embed_model=embeddings, llm=llm)

# 不用set_global_service_context会报错，会引用OpenAI的模型
set_global_service_context(service_context)

# base_index = VectorStoreIndex(base_nodes)
# base_retriever = base_index.as_retriever(similarity_top_k=2)
# query_engine = RetrieverQueryEngine.from_args(
#    base_retriever, service_context=service_context)
#
# response = query_engine.query(
#    "Can you tell me about the key concepts for safety finetuning")


sub_node_parsers = [
    SimpleNodeParser.from_defaults(chunk_size=c, chunk_overlap=64) for c in sub_chunk_sizes
]

all_nodes = []

for base_node in base_nodes:
    for n in sub_node_parsers:
        sub_nodes = n.get_nodes_from_documents([base_node])
        sub_inodes = [
            IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
        ]
        all_nodes.extend(sub_inodes)
    original_node = IndexNode.from_text_node(base_node, base_node.node_id)
    all_nodes.append(original_node)

all_nodes_dict = {n.node_id: n for n in all_nodes}

print(all_nodes_dict)
