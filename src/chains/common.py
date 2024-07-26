from langchain_core.runnables import chain


@chain
def global_data(inp: dict):
    from datetime import datetime
    inp['date'] = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    inp['week'] = datetime.now().strftime("%A")
    return inp
