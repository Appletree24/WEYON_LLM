# CosyVoice音频生成脚本

#!/bin/bash
source /home/kemove/miniconda3/etc/profile.d/conda.sh
set -e

export CUDA_VISIBLE_DEVICES=$5
# 语音合成前端
export PYTHONPATH=/home/kemove/AI_Projects/CosyVoice/third_party/Matcha-TTS

if [ $# -lt 2 ]; then
    echo "必须提供要生成的语音文本以及生成音频文件的名称"
    exit 1
fi

cd ~/AI_Projects/CosyVoice
conda activate cosyvoice

echo cosyvoice_stream.py --txt "$1" --name "$2" --description "$3" --spk_kind "$4"

python cosyvoice_stream.py --txt "$1" --name "$2" --description "$3" --spk_kind "$4"

if [ $? -eq 0 ]; then
    echo "CosyVoice generate $2-$3.wav done"
else
    echo "CosyVoice generate $2-$3.wav failed"
    exit 1
fi
