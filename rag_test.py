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

embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"
documents = SimpleDirectoryReader(
    input_dir="index_project/dataFiles").load_data(show_progress=True)

node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)

base_nodes = node_parser.get_nodes_from_documents(documents=documents)

embeddings = ModelScopeEmbeddings4LlamaIndex(model_id=embedding_model)
llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:8000/v1",
                 api_key="dummy", max_tokens=100)

service_context = ServiceContext.from_defaults(embed_model=embeddings, llm=llm)
set_global_service_context(service_context)

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

response = query_engine.query("湖南科技大学毕业生总人数是多少?")

print(response)


# pdf_reader = PyMuPDFReader()
#
# documents = pdf_reader.load_data(file_path='/home/kemove/zzh/index_project/1.pdf',metadata=True)
# for doc in documents:
#    doc.text = doc.text.decode()
# print(documents[0])

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# model_name_or_path = "/home/kemove/model/qwen/Qwen2-72B-Instruct"
#
# Settings.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
# model = AutoModelForCausalLM.from_pretrained(model_name_or_path,device_map="auto",torch_dtype=torch.bfloat16)
