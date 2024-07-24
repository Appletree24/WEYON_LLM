#!//home/kemove/miniconda3/envs/llm/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :CustomRetriever.py
# @Time      :2024/07/23 15:44:01
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 混合检索器
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore

from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)

from typing import List


class CustomRetriever(BaseRetriever):
    def __init__(self, vector_retriever: VectorIndexRetriever, keyword_retriever: KeywordTableSimpleRetriever, mode: str = "AND") -> None:
        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("mode must be 'AND' or 'OR'")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        keyword_nodes = self._keyword_retriever.retrieve(query_bundle)
        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}
        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})
        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)
        retrieve_nodes = [combined_dict[r_id] for r_id in retrieve_ids]
        return retrieve_nodes
