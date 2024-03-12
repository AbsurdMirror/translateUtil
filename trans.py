from pynput.keyboard import Controller, Key, Listener 
import pyperclip
import json
import requests
import os  

###### 全局变量 ######
ctrl_c_times = 0
exit_progress = False

hasSetting = False
setting = {}

f = open("CaiYunXiaoYi.token")
CaiYunXiaoYiToken = f.read()

def tranlateCaiYunXiaoYi(source, direction):
    url = "http://api.interpreter.caiyunai.com/v1/translator"

    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token

    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }

    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + CaiYunXiaoYiToken,
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    return json.loads(response.text)["target"]

def split_string_by_english_sentences(input_string):  
    # 将换行符替换为空格  
    input_string_no_newline = input_string.replace('\r', ' ')
    input_string_no_newline = input_string_no_newline.replace('\n', ' ')

    import nltk
    sentences = nltk.sent_tokenize(input_string_no_newline)

    return input_string_no_newline, sentences
  
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

        os.system('cls')
        print(f"剪切板内容: {clipboard_content} \n")
        print(f"去除换行: {no_newline_content} \n")
        print(f"句子拆分: {tranlate_source_formatted} \n")
        print(f"翻译结果: {tranlate_target_formatted} \n")
        # print(f"Clipboard content: {clipboard_content} \n")
        # print(f"No newline content: {no_newline_content} \n")
        # print(f"Translation source: {tranlate_source_formatted} \n")
        # print(f"Translation target: {tranlate_target_formatted} \n")

        if hasSetting :
            if setting["save"]["isSave"]:
                fileDirpath = os.path.join("./save", setting["save"]["savePath"])
                if not os.path.exists(fileDirpath):  
                    os.makedirs(fileDirpath)
                filePath = os.path.join(fileDirpath, setting["save"]["saveName"])
                with open(filePath, "a", encoding="utf-8") as savefile:
                    for item in tranlate_target:
                        # 将每一项写入文件，并在每一项后添加一个换行符  
                        savefile.write(item + '\n')
                    savefile.write("---\n")

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


############################################################################################################

############################################
# 设置文件名  
filename = 'setting.json'  

# 检查文件是否存在  
if os.path.exists(filename):  
    # 打开文件并读取内容  
    with open(filename, 'r') as file:  
        # 解析JSON内容为对象/字典
        setting = json.load(file)
        hasSetting = True
else:  
    print(f"文件 {filename} 不存在")
############################################

# 使用with语句来确保Listener正确关闭  
with Listener(on_press=on_press, on_release=on_release) as listener:  
    listener.join()

while(not exit_progress) :
    a = 1