"""
启动入口
"""
from langchain_core.runnables import Runnable

from chains import simple_chain
from basic import default_context

_ = simple_chain


def simple_chain(message, history):
    chain: Runnable = default_context['simple_chain']
    partial_message = ""
    for chunk in chain.stream(message):
        partial_message = partial_message + chunk.content
        yield partial_message


import gradio as gr

if __name__ == "__main__":
    gr.ChatInterface(simple_chain).launch(share=True)
