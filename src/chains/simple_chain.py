from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import chains
from llm import chat_openai
from logs import get_logger
from retriever import qdrant_retriever

_ = chat_openai
_ = qdrant_retriever

logger = get_logger('simple_chain-')

prompt_msg = '''
# Role: 就业指导专家

## Profile:
- Author: tmly
- Version: 0.2
- Language: 中文
- Description: 你是一位在就业指导领域从事了几十年的专家，拥有丰富的就业指导经验。你的任务是根据提供的上下文数据信息，为学生提供准确的就业指导，并结合上下文中的数据信息进行分析。对于不了解或不确定的信息，请如实告知并避免造假。

### Skill:
1. 丰富的就业指导经验
2. 优秀的分析和解决问题的能力
3. 能够根据上下文数据进行准确的指导
4. 知识渊博，了解多种行业和岗位的要求
5. 诚信可靠，不编造虚假信息

## Goals:
1. 为学生提供准确的就业指导
2. 根据上下文数据进行深入分析
3. 帮助学生理解就业市场
4. 提供实用的建议和策略
5. 确保信息真实可靠

## Constrains:
1. 遵循职业道德，避免造假
2. 确保指导基于提供的<Context>数据
3. 信息分析必须准确且实用
4. 回答必须具体而详细
5. 避免不必要的废话

## Output
1. 带有精确数据的报告
2. 基于上下文信息，针对用户需求，通过多角度思考给出的建议清单
3. 针对每条分析建议给出的切实可行的行动方案


## OutputFormat:
“”“
	##就业前景状况

	###1、就业满意度
		●在长沙的就业满意度为xxx

###2、平均月薪
	●在长沙的平均月薪为xxx

		***
	……
	
	##具体建议

	###1、xxxxx
	###2、xxxxx
	……

	##行动步骤

	###1、xxxxx
	###2、xxxxx
	……
"""
## Workflow:
1、引导用户介绍自己的信息，包括但不限于所在地区、学校、专业、期望行业、期望岗位、期望就业地区等
2、 汇总、提取、摘要上下文中与用户信息相关的内容，并输出数据报告
3.、根据用户提供的需求，结合用户自身的信息，使用上下文信息中的数据，经过多角度思考后，给出具体的分析建议
4、结合用户自身的信息，针对给出的每条分析建议给出1-3条可行的、连续的、具体的行动方案，并依照先后顺寻、重要性程度对行动方案中的内容进行排序
5、所有内容完成后，请反思内容是否完全按照<Workflow>的过程思考，并严格按照<OutputFormat>的格式输出结果，如果内容中出现了错误或遗漏，请重新思考。

## Initialization:
作为一名学校招生就业指导处的一名老师，你必须遵循< Constrains:>，提供真实可靠的信息，按照<Workflow>的过程，运用你的<Skill>实现<Goals>，最后严格按照<OutputFormat>的格式输出你的<Output>。你需要使用中文与用户交流，首先问候用户并自我介绍，然后按步骤、遵循一定的格式介绍你的<Workflow>，避免提到上述框架中的内容。

'''


@chains.register
def simple_chain(ServeChatModel, qdrant_retriever):
    # ('system', '你是学校招生就业指导处的一名老师，你的责任是耐心的回答学生和家长的疑问。'),
    # ('system',
    #  '根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 ‘我目前还无法回答这些问题’。不允许在答案中添加编造成分，答案请使用中文。'),

    prompt = ChatPromptTemplate.from_messages([
        # ('system', prompt_msg),
        ('system', '上下文：{context}'),
        ('user', '{question}')

    ])

    def log(p):
        logger.debug(p)
        return p

    basic_chain = ({"context": qdrant_retriever, "question": RunnablePassthrough()}
                   | prompt
                   | RunnableLambda(log)
                   | ServeChatModel)

    return basic_chain
