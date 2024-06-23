from unittest import TestCase

from langchain_core.runnables import Runnable

from chains import simple_chain
from basic import default_context

_ = simple_chain


class Test(TestCase):
    def test_simple_chain(self):
        chain: Runnable = default_context['simple_chain']
        for chunk in chain.stream("git 如何使用?"):
            print(chunk.content, end="")
