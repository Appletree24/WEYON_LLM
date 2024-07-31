#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Shell_split.py
# @Time      :2024/07/29 11:39:59
# @Author    : 张子辉， 颜淳羲，熊鑫
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 将数字人脚本中的音频生成与视频生成独立,最后再合成
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

import os
from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess
import io

app = Flask(__name__)
CORS(app)  # 启用CORS

AUDIO_PREFIX = "/home/kemove/AI_Projects/AutomaticScript/audio/"
VIDEO_PREFIX = "/home/kemove/AI_Projects/metahuman-stream/wav2lip/"
VIDEO_INPUT = "/home/kemove/AI_Projects/AutomaticScript/video/"
VIDEO_CONDA_ENV = "nerfstream"
OUTPUT_PATH = "/home/kemove/AI_Projects/AutomaticScript/results/"
TONE_PROMPT_PATH = "/home/kemove/AI_Projects/AutomaticScript/Tone-Prompt.txt"


def is_tone_prompt_empty() -> bool:
    return os.stat(TONE_PROMPT_PATH).st_size == 0


def tone_prompt_process() -> None:
    seen_descriptions = set()
    lines_to_keep = []

    with open(TONE_PROMPT_PATH, 'r') as infile:
        for line in infile:
            _, description = line.strip().split(' - ')
            if description not in seen_descriptions:
                seen_descriptions.add(description)
                lines_to_keep.append(description)

    with open(TONE_PROMPT_PATH, 'w') as outfile:
        for i, description in enumerate(lines_to_keep):
            outfile.write(f"{i} - {description}\n")


@app.route('/', methods=['POST'])
def handle_post():
    print("本次的请求为：", request)
    data = request.get_json()
    print("本次的请求体为：", data)
    txt = data['txt']
    name = data['name']
    description = data['description']
    video_path = ""
    spk_id = data['spk_id']
    last_line_number = ""
    # if video_path.__contains__(" "):
    #     raise ValueError("视频素材路径不能包含空格")
    if os.path.isfile("Tone-Prompt.txt"):
        if is_tone_prompt_empty():
            with open("Tone-Prompt.txt", 'w') as f:
                f.write(f"0 - {description}\n")
                last_line_number = 0
        else:
            with open("Tone-Prompt.txt", 'r') as f:
                lines = f.readlines()
                last_line_number = lines[-1].split(" ")[0]

        with open("Tone-Prompt.txt", 'a') as f:
            f.write(f"{int(last_line_number)+1} - {description}\n")
            last_line_number = str(int(last_line_number) + 1)
    else:
        with open("Tone-Prompt.txt", 'w') as f:
            f.write(f"0 - {description}\n")
            last_line_number = 0
    tone_prompt_process()
    if os.path.isfile(VIDEO_INPUT + name + ".mp4"):
        video_path = VIDEO_INPUT + name + ".mp4"
    else:
        video_path = VIDEO_PREFIX + "old.mp4"
    # video_path = VIDEO_PREFIX + "old.mp4"
    audio_path = AUDIO_PREFIX + name + "-" + description + ".wav"
    output = OUTPUT_PATH + name + "-" + str(last_line_number) + ".mp4"
    if txt == "":
        raise ValueError("生成文本不能为空")
    if name == "":
        raise ValueError("生成文件名不能为空")
    if video_path == "":
        raise ValueError("视频素材路径不能为空")
    os.system("chmod +x ./Audio_generate.sh")
    audio_result = subprocess.run(['./Audio_generate.sh', txt, name,
                                   description, spk_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if audio_result.returncode == 0:
        print("音频生成成功")
        audio_path = "'" + audio_path + "'"
        temp_replace_path = "'"+audio_path.replace(
            description, str(last_line_number))+"'"
        os.system(
            f"mv {audio_path} {temp_replace_path}")
    else:
        print("音频生成失败")
        print("报错信息为：", audio_result.stderr.decode())
        raise ValueError("音频生成失败")
    os.system("chmod +x ./Video_generate.sh")
    audio_path = AUDIO_PREFIX + name + "-" + str(last_line_number) + ".wav"
    video_command = f"source /home/kemove/miniconda3/etc/profile.d/conda.sh && conda activate {VIDEO_CONDA_ENV} && export CUDA_VISIBLE_DEVICES=2 && cd ~/AI_Projects/Wav2Lip && python inference.py --checkpoint_path ./checkpoints/wav2lip.pth --face {video_path} --audio {audio_path} --outfile {output}"
    video_result = subprocess.run(video_command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, executable="/bin/bash")
    if video_result.returncode == 0:
        print("视频生成成功")
    else:
        print("视频生成失败")
        print("报错信息为：", video_result.stderr.decode())
        raise ValueError("视频生成失败")
    mp4_file = io.BytesIO()
    with open(output, 'rb') as f:
        mp4_file.write(f.read())
    mp4_file.seek(0)
    description = "'"+description+"'"
    os.system(
        f"mv {output} ./results/{name}-{description}.mp4")
    os.system(
        f"mv ./audio/{name}-{last_line_number}.wav ./audio/{name}-{description}.wav")
    return send_file(mp4_file, mimetype='video/mp4', as_attachment=True, download_name="video")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5219, debug=True)
