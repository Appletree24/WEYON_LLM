"""
启动入口
"""
from langchain_core.runnables import Runnable

from chains import simple_chain
from basic import default_context

_ = simple_chain


def simple_chain():
    chain: Runnable = default_context['simple_chain']
    for chunk in chain.stream("git 如何使用?"):
        print(chunk.content, end="")


if __name__ == "__main__":
    simple_chain()