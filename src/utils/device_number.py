#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :device_number.py
# @Time      :2024/07/21 09:22:11
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 方便获取显卡在不同总线模式下的编号
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。
import torch
import os


def get_FASTEST_FIRST_ID():
    for i in range(torch.cuda.device_count()):
        if torch.cuda.is_available():
            print("GPU 编号: {}".format(i))
            print("GPU 名称: {}".format(torch.cuda.get_device_name(i)))
        else:
            print("设备上没有可用的GPU")


def change_to_PCI_BUS_ID():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"


def change_to_FASTEST_FIRST():
    os.environ["CUDA_DEVICE_ORDER"] = "FASTEST_FIRST"
