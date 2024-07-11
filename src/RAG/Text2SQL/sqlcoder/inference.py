#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :inference.py
# @Time      :2024/07/05 14:41:42
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: SQLCoder启动代码
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import argparse
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'


def generate_prompt(question, prompt_file="WEYON_LLM/RAG/Text2SQL/sqlcoder/prompt.md", metadata_file="WEYON_LLM/RAG/Text2SQL/sqlcoder/ai_use.sql"):
    with open(prompt_file, "r") as f:
        prompt = f.read()

    with open(metadata_file, "r") as f:
        table_metadata_string = f.read()

    prompt = prompt.format(
        user_question=question, table_metadata_string=table_metadata_string
    )
    return prompt


def get_tokenizer_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        use_cache=True,
    )
    return tokenizer, model


def run_inference(question, prompt_file="WEYON_LLM/RAG/Text2SQL/sqlcoder/prompt.md", metadata_file="WEYON_LLM/RAG/Text2SQL/sqlcoder/ai_use.sql"):
    tokenizer, model = get_tokenizer_model("defog/sqlcoder-7b-2")
    prompt = generate_prompt(question, prompt_file, metadata_file)

    # make sure the model stops generating at triple ticks
    # eos_token_id = tokenizer.convert_tokens_to_ids(["```"])[0]
    eos_token_id = tokenizer.eos_token_id
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        do_sample=False,
        # added return_full_text parameter to prevent splitting issues with prompt
        return_full_text=False,
        num_beams=5,  # do beam search with 5 beams for high quality results
    )
    generated_query = (
        pipe(
            prompt,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
        )[0]["generated_text"]
        .split(";")[0]
        .split("```")[0]
        .strip()
        + ";"
    )
    return generated_query


if __name__ == "__main__":
    # Parse arguments
    _default_question = "Tell me the table's name"
    parser = argparse.ArgumentParser(description="Run inference on a question")
    parser.add_argument("-q", "--question", type=str,
                        default=_default_question, help="Question to run inference on")
    args = parser.parse_args()
    question = args.question
    print("Loading a model and generating a SQL query for answering your question...")
    print(run_inference(question))
