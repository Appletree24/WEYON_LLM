import os
from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
import io
import threading
import datetime
import subprocess
import uuid
import time
app = Flask(__name__)
CORS(app)  # 启用CORS
content_dir = {}

AUDIO_PREFIX = "/home/kemove/AI_Projects/AutomaticScript/audio/"
VIDEO_PREFIX = "/home/kemove/AI_Projects/metahuman-stream/wav2lip/"
VIDEO_INPUT = "/home/kemove/AI_Projects/AutomaticScript/video/"
VIDEO_CONDA_ENV = "nerfstream"
OUTPUT_PATH = "/home/kemove/AI_Projects/AutomaticScript/results/"
TONE_PROMPT_PATH = "/home/kemove/AI_Projects/AutomaticScript/Tone-Prompt.txt"
BG_REPLACE_VIDEO_PATH = "/home/kemove/AI_Projects/AutomaticScript/bg_replace_video/"
BG_PIC_PATH = "/home/kemove/AI_Projects/AutomaticScript/background_img/"

# 查询显存


def get_gpu_utilization():
    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used',
                            '--format=csv,noheader,nounits'], stdout=subprocess.PIPE)
    memory_usage = result.stdout.decode('utf-8').strip().split('\n')
    print("111\n")
    return [int(mem) for mem in memory_usage]


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


def process_task(txt: str, name: str, description: str, spk_id: str, bg_replace: int, video_format: str, img_format: str):
    """
    txt: str 存放文本信息。
    name: str 存放uuid，task_id。
    description: str 存放对语气的描述。
    spk_id: str “中文男”、“中文女”、
    bg_replace: int 是否需要更换背景，0不用， 1需要更换背景
    video_format: str 视频格式 如“.mp4”， “.avi”
    img_format: str 图片格式 如“.jpg”，“png”
    """
    if txt == "":
        raise ValueError("生成文本不能为空")
    if name == "":
        raise ValueError("生成文件名不能为空")
    CUDA_ID = -1

    # 判断显卡是否空闲，如果没有空闲就等待 5 秒。其中 4 号与 5 号是 A100 不要去使用
    # 4号和5号和Nvidia-smi输出对不上，正常，因为两边总线顺序不一样,Pytorch是FASTEST-FIRST，NVIDIA-SMI是PCIE
    while CUDA_ID == -1:
        gpu_utilizations = get_gpu_utilization()
        for i, utilization in enumerate(gpu_utilizations):
            if i in [4, 5]:
                continue
            print(f"GPU {i} memory_usage: {utilization}MiB")
            if utilization <= 2000:
                CUDA_ID = i
                break
        if (CUDA_ID == -1):
            print("没有可用的GPU，显存使用率低于2000mib, 5秒后重新检查。")
            time.sleep(5)  # 等待 10 秒后重新检查
    print(CUDA_ID, "\n")
    command = f"export CUDA_VISIBLE_DEVICES={CUDA_ID}"
    subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, executable="/bin/bash")
    # 处理数字人视频
    video_path = ""
    last_line_number = ""
    if os.path.isfile("Tone-Prompt.txt"):
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
    if os.path.isfile(VIDEO_INPUT + name + video_format):
        video_path = VIDEO_INPUT + name + video_format
    else:
        video_path = VIDEO_PREFIX + "old.mp4"
    # 替换背景
    if bg_replace == 1:
        bg_file_path = BG_PIC_PATH + name + img_format
        replace_result = subprocess.run(
            ['./BG_Replace', video_path, bg_file_path])
        if replace_result.returncode == 0:
            print("背景替换成功")
            # ffmpeg -i output.avi -vcodec libx264 -acodec aac output.mp4
            video_path = BG_REPLACE_VIDEO_PATH + name + video_format
            bg_command = f"source /home/kemove/miniconda3/etc/profile.d/conda.sh && conda deactivate && ffmpeg -i output.avi -vcodec libx264 -acodec aac {video_path}"
            convert_result = subprocess.run(bg_command, shell=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, executable="/bin/bash")
            if convert_result.returncode == 0:
                print("视频格式转换成功")
            else:
                raise RuntimeError("视频格式转换失败")
        else:
            raise RuntimeError("背景替换失败")
    else:
        print("本次不需要替换背景")
    audio_path = AUDIO_PREFIX + name + "-" + description + ".wav"
    output = OUTPUT_PATH + name + "-" + \
        str(last_line_number) + video_format  # 最终生成的数字人输出的文件位置
    os.system("chmod +x ./Audio_generate.sh")
    audio_result = subprocess.run(['./Audio_generate.sh', txt, name,
                                   description, spk_id, str(CUDA_ID)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    video_command = f"source /home/kemove/miniconda3/etc/profile.d/conda.sh && conda activate {VIDEO_CONDA_ENV} && export CUDA_VISIBLE_DEVICES={CUDA_ID} && cd ~/AI_Projects/Wav2Lip && python inference.py --checkpoint_path ./checkpoints/wav2lip.pth --face {video_path} --audio {audio_path} --outfile {output}"
    video_result = subprocess.run(video_command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, executable="/bin/bash")
    if video_result.returncode == 0:
        print("视频生成成功")
    else:
        print("视频生成失败")
        print("报错信息为：", video_result.stderr.decode())
        raise ValueError("视频生成失败")
    description = "'"+description+"'"
    os.system(
        f"mv {output} ./results/{name}-{description}{video_format}")
    os.system(
        f"mv ./audio/{name}-{last_line_number}.wav ./audio/{name}-{description}.wav")


@app.route('/dp-api/create-video', methods=['POST'])
def create_video():
    data = request.get_json()
    name = data['task_id']
    txt = data["text"]
    description = data['description']
    bg_replace = data['bg_replace']
    video_format = data['video_format']
    img_format = data['img_format']
    spk_id = data['spk_id']
    json_task_data = {
        "txt": txt,
        "description": description,
        "bg_replace": bg_replace,
        "video_format": video_format,
        "img_format": img_format
    }
    content_dir[name] = json_task_data
    thread = threading.Thread(
        target=process_task, args=(txt, name, description, spk_id, bg_replace, video_format, img_format))
    thread.start()

    return "success"


@app.route('/dp-api/create-task', methods=['POST'])
def create_task():
    f = ''
    f_img = ''
    f_path = ''
    f_img_path = ''
    img_format = ''
    video_format = ''
    f_name = str(uuid.uuid1())
    bg_replace = 0
    if 'selectedFiles' in request.files:
        f = request.files['selectedFiles']
        video_format = '.' + f.filename.split('.')[-1]
        f_path = VIDEO_INPUT + f_name + video_format
        f.save(f_path)
    if 'backgroundImg' in request.files:
        f_img = request.files['backgroundImg']
        img_format = '.' + f_img.filename.split('.')[-1]
        f_img_path = BG_PIC_PATH + f_name + img_format
        f_img.save(f_img_path)
        bg_replace = 1

    print(f_name, video_format, img_format)
    return jsonify({
        "task_id": f_name,
        "bg_replace": bg_replace,
        "video_format": video_format,
        "img_format": img_format
    })


@app.route('/static/<filename>', methods=['POST'])
def get_video(filename):
    data = request.get_json()
    name = data['task_id']
    video_format = content_dir[name]['video_format']
    video_path = OUTPUT_PATH + filename + video_format
    video_file = io.BytesIO()
    with open(video_path, 'rb') as f:
        video_file.write(f.read())
    video_file.seek(0)
    del content_dir[name]
    ###如果要进行用户管理则将del 更改成为将用户数据存放文件或数据库中 请勿存放在栈区 防止内存泄漏 
    return send_file(video_file, mimetype='video/' + video_format[:1], as_attachment=True, download_name="video")


@app.route('/dp-api/get-task', methods=['POST'])
def get_task():
    print(request)
    data = request.get_json()
    print(data)
    name = data['task_id']
    description = content_dir[name]['description']
    video_format = content_dir[name]['video_format']
    # 将task_id转换成为具体的文件名称 将文件名称
    filename = name + "-" + description
    # 生成的文件所在路径
    path = OUTPUT_PATH + filename + video_format
    call_back_data = """"""
    if not os.path.exists(path):
        print("数字人尚未生成")
        # 返回文件状态运行中
        call_back_data = {
            "content_text": content_dir[name]['txt'],
            "dp_mp4_url": "",
            "status": "generating",
            "task_id": name
        }
    else:
        print("数字人生成成功")
        call_back_data = {
            "content_text": content_dir[name]['txt'],
            "dp_mp4_url": "/static/" + filename,
            "status": "Created",
            "task_id": name
        }
    # 将call_back_json作为响应数据返回
    response = make_response(jsonify(call_back_data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Server'] = 'Werkzeug/3.0.2 Python/3.10.14'
    response.headers['Date'] = datetime.datetime.now().strftime(
        '%a, %d %b %Y %H:%M:%S GMT')
    response.headers['trace_id'] = name
    response.headers['Connection'] = 'close'
    return response


@app.route('/dp-api/task-callback', methods=['POST'])
def task_callback():
    print(request)
    data = request.get_json()
    print(data)
    name = data['task_id']
    description = content_dir[name]['description']
    video_format = content_dir[name]['video_format']
    # 将task_id转换成为具体的文件名称 将文件名称
    filename = name + "-" + description
    # 生成的文件所在路径
    path = OUTPUT_PATH + filename + video_format
    call_back_data = """"""
    if not os.path.exists(path):
        print("数字人尚未生成")
        # 返回文件状态运行中
        call_back_data = {
            "content_text": content_dir[name]['txt'],
            "dp_mp4_url": "",
            "status": "generating",
            "task_id": name
        }
    else:
        call_back_data = {
            "content_text": content_dir[name]['txt'],
            "dp_mp4_url": "/static/" + filename,
            "status": "Created",
            "task_id": name
        }
    # 将call_back_json作为响应数据返回
    response = make_response(jsonify(call_back_data))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Server'] = 'Werkzeug/3.0.2 Python/3.10.14'
    response.headers['Date'] = datetime.datetime.now().strftime(
        '%a, %d %b %Y %H:%M:%S GMT')
    response.headers['trace_id'] = name
    response.headers['Connection'] = 'close'
    return response


@app.route('/', methods=['POST'])
def handle_post():
    return


if __name__ == '__main__':
    tone_dict = {}
    app.run(host='0.0.0.0', port=5218, debug=True)

 # 第一个参数是需要接入数字人的文本，第二个输入时保存的文件名称
