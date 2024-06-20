from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.models import Model

model_id = "iic/nlp_gte_sentence-embedding_chinese-base"

pipeline_se = pipeline(
    Tasks.sentence_embedding,
    model=model_id,
    sequence_length=512)

inputs = {
    "source_sentence": ["吃完海鲜可以喝牛奶吗？"],
    "sentences_to_compare": [
        "不可以，早晨喝牛奶不科学",
        "吃了海鲜后是不能再喝牛奶的，因为牛奶中含得有维生素C，如果海鲜喝牛奶一起服用会对人体造成一定的伤害",
        "吃海鲜是不能同时喝牛奶吃水果，这个至少间隔6小时以上才可以。",
        "吃海鲜是不可以吃柠檬的因为其中的维生素C会和海鲜中的矿物质形成砷"
    ]
}

result = pipeline_se(inputs)
print(result)
