import os
import sys
import json
from deepseek_api import group_sentences_to_paragraphs as deepseek_group_sentences_to_paragraphs
from zhipu_api import group_sentences_to_paragraphs as zhipu_group_sentences_to_paragraphs

def group_sentences_to_paragraphs(message_value, ai_model):
    # 读取配置文件
    file_path = os.path.dirname(os.path.abspath(__file__))
    
    # 根据配置选择调用的 API
    if ai_model == "deepseek":
        return deepseek_group_sentences_to_paragraphs(message_value)
    elif ai_model == "zhipu":
        return zhipu_group_sentences_to_paragraphs(message_value)
    else:
        raise ValueError("Invalid API selection in config.json. Please specify 'deepseek' or 'zhipu'.")

# 示例调用
if __name__ == "__main__":
    # 读取待处理的句子
    file_path = os.path.dirname(os.path.abspath(__file__))
    message_path = os.path.join(file_path, "test.txt")
    with open(message_path, "r", encoding="utf-8") as f:
        message_value = f.read()

    # 调用函数
    ai_response = group_sentences_to_paragraphs(message_value)
    print(ai_response)