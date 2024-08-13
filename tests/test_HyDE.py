from unittest import TestCase

from langchain_core.runnables import Runnable

from basic import default_context
from chains import HyDE

_ = HyDE


class Test(TestCase):
    def test_hy_de(self):
        test_chain: Runnable = default_context.get_bean('hy_de')
        res = test_chain.invoke({'question': '2023年长沙理工大学的就业情况'})
        self.assertIsInstance(obj=res, cls=HyDE.HypotheticalDocument)
