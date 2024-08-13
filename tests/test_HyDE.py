from unittest import TestCase

from langchain_core.documents import Document
from langchain_core.runnables import Runnable

from basic import default_context
from chains import HyDE

_ = HyDE


class Test(TestCase):
    def test_hy_de(self):
        test_chain: Runnable = default_context.get_bean('hy_de')
        res = test_chain.invoke({'question': '2023年长沙理工大学的就业情况'})
        self.assertIsInstance(obj=res, cls=HyDE.HypotheticalDocument)

    def test_hyde_rag(self):
        test_chain: Runnable = default_context.get_bean('hyde_rag')
        res: list[Document] = test_chain.invoke({'question': '2023年长沙理工大学的就业情况'})
        self.assertIsNotNone(res)
        for i, re in enumerate(res):
            print(f"第{i}篇文档：\n{re.page_content}\n")
