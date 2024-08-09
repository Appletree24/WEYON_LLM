from unittest import TestCase

from langchain_core.runnables import Runnable

from basic import default_context
from chains import simple_chain

_ = simple_chain


class Test(TestCase):
    def test_simple_chain(self):
        chain: Runnable = default_context['simple_chain']
        res = chain.invoke("git 如何使用?")
        self.assertIsNotNone(str(res))

    def test_simple_rag(self):
        chain: Runnable = default_context['simple_rag']
        prompt = chain.invoke("git 如何使用?")
        self.assertIsNotNone(prompt)
