from pynput.keyboard import Controller, Key, Listener 
import traceback
import time
import pyperclip
import json
import requests
import re  

def tranlateCaiYunXiaoYi(source, direction):
    url = "http://api.interpreter.caiyunai.com/v1/translator"

    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token
    token = "??????"

    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }

    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + token,
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    return json.loads(response.text)["target"]
  

def split_string_by_english_sentences(input_string):  
    # 将换行符替换为空格  
    input_string_no_newline = input_string.replace('\r', ' ')
    input_string_no_newline = input_string_no_newline.replace('\n', ' ')

    # # 匹配英文句子结束的标志，但排除缩写后的点  
    # sentence_endings = r"""  
    #     (?<=[.!?])                # 确保点、问号或感叹号前面有字符（避免缩写）  
    #     (?<!\w\.\w\.)             # 避免诸如 "Mr." 或 "Dr." 这样的缩写  
    #     [.!?]+                     # 一个或多个点、问号或感叹号  
    #     (?=\s+|$)                  # 确保后面有空白或字符串结束  
    # """  
    # sentence_endings = re.compile(sentence_endings, re.VERBOSE | re.IGNORECASE)  
      
    # # 使用re模块的split方法按照模式拆分字符串  
    # sentences = sentence_endings.split(input_string_no_newline)  
    import nltk
    sentences = nltk.sent_tokenize(input_string_no_newline)

    # # 移除拆分后数组中的空字符串，并去除句子两端的空白  
    # sentences = [s.strip() for s in sentences if s.strip()]  
      
    return input_string_no_newline, sentences

# 全局变量，用于存储按下ctrl + d键的次数  
ctrl_c_times = 0
exit_progress = False
  
def on_press(key):
    global ctrl_c_times
    global exit_progress

    # print(key)
    if str(key) == r"'\x03'":
        ctrl_c_times = ctrl_c_times + 1
    else:
        ctrl_c_times = 0

    if str(key) == r"'\x0f'" or ctrl_c_times == 2:
        # print("(ctrl + o) || ((ctrl + c) * 2)")

        clipboard_content = pyperclip.paste()
        no_newline_content, tranlate_source = split_string_by_english_sentences(clipboard_content)
        # tranlate_target = []
        tranlate_target = tranlateCaiYunXiaoYi(tranlate_source, "auto2zh")
        tranlate_source_formatted = json.dumps(tranlate_source, indent=4, ensure_ascii=False)
        tranlate_target_formatted = json.dumps(tranlate_target, indent=4, ensure_ascii=False)  

        print(f"剪切板内容: {clipboard_content} \n")
        print(f"去除换行: {no_newline_content} \n")
        print(f"句子拆分: {tranlate_source_formatted} \n")
        print(f"翻译结果: {tranlate_target_formatted} \n")\
        # print(f"Clipboard content: {clipboard_content} \n")
        # print(f"No newline content: {no_newline_content} \n")
        # print(f"Translation source: {tranlate_source_formatted} \n")
        # print(f"Translation target: {tranlate_target_formatted} \n")

        ctrl_c_times = 0
    
    if str(key) == r"'\x1a'":
        # 结束程序
        print("End program")
        listener.stop()
        exit_progress = True
  
def on_release(key):  
    global ctrl_pressed  
    if key == Key.ctrl:  
        ctrl_pressed = 0  

# 使用with语句来确保Listener正确关闭  
with Listener(on_press=on_press, on_release=on_release) as listener:  
    listener.join()

while(not exit_progress) :
    a = 1