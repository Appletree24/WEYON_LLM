# name: config_util.py
# description: 辅助配置文件
# author: acxgdxy
# time: 2024/07/02
import codecs
import json
import os
from configparser import ConfigParser

config: json = None
system_config: ConfigParser = None
key_ali_nls_key_id = None
key_ali_nls_key_secret = None
key_ali_nls_app_key = None
key_ngrok_cc_id = None
key_gpt_api_key = "xxx"
key_gpt_tts_key = None
gpt_base_url = "http://192.168.100.111:8001/v1"
gpt_tts_base_url = None
ASR_mode = None
local_asr_ip = None
local_asr_port = None
gpt_model_engine = "qwen2-pro"
tavily_api_key = "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"
key_ms_tts_key = None
key_ms_tts_region = None
tts_module = None
proxy_config = None
max_history_num = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 读取配置文件


def load_config():
    global config
    global system_config
    # global key_ali_nls_key_id
    # global key_ali_nls_key_secret
    # global key_ali_nls_app_key
    # global key_ngrok_cc_id
    global key_gpt_api_key
    # global key_gpt_tts_key
    global gpt_base_url
    # global gpt_tts_base_url
    # global key_ms_tts_key
    # global key_ms_tts_region
    # global tts_module
    global tavily_api_key
    global ASR_mode
    global local_asr_ip
    global local_asr_port
    # global proxy_config
    global gpt_model_engine
    global max_history_num

    system_config = ConfigParser()
    # print(os.path.join(BASE_DIR, 'mySystem.conf'))
    system_config.read(os.path.join(
        BASE_DIR, 'mySystem.conf'), encoding='UTF-8')
    # print(system_config['key'])
    # key_ali_nls_key_id = system_config.get('key', 'ali_nls_key_id')
    # key_ali_nls_key_secret = system_config.get('key', 'ali_nls_key_secret')
    # key_ali_nls_app_key = system_config.get('key', 'ali_nls_app_key')
    # key_ngrok_cc_id = system_config.get('key', 'ngrok_cc_id')
    key_gpt_api_key = system_config.get('key', 'gpt_api_key')
    # key_gpt_tts_key = system_config.get('key', 'gpt_tts_key')
    gpt_base_url = system_config.get('key', 'gpt_base_url')
    # gpt_tts_base_url = system_config.get('key', 'gpt_tts_base_url')
    # key_ms_tts_key = system_config.get('key', 'ms_tts_key')
    # key_ms_tts_region  = system_config.get('key', 'ms_tts_region')
    # tts_module  = system_config.get('key', 'tts_module')
    # ASR_mode = system_config.get('key', 'ASR_mode')
    # local_asr_ip = system_config.get('key', 'local_asr_ip')
    # local_asr_port = system_config.get('key', 'local_asr_port')
    # proxy_config = system_config.get('key', 'proxy_config')
    gpt_model_engine = system_config.get('key', 'gpt_model_engine')
    tavily_api_key = system_config.get('key', 'tavily_api_key')
    max_history_num = system_config.get('key', 'max_history_num')
    # print(os.path.join(BASE_DIR, 'config.json'))
    config = json.load(codecs.open(os.path.join(
        BASE_DIR, 'config.json'), encoding='utf-8'))


def save_config(config_data):
    global config
    config = config_data
    file = codecs.open('config.json', mode='w', encoding='utf-8')
    file.write(json.dumps(config, sort_keys=True,
                          indent=4, separators=(',', ': ')))
    file.close()
    # for line in json.dumps(config, sort_keys=True, indent=4, separators=(',', ': ')).split("\n"):
    #     print(line)
