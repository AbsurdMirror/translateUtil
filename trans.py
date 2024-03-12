from pynput.keyboard import Controller, Key, Listener 
import pyperclip
import json
import requests
import os  
import tkinter as tk  
from tkinter import scrolledtext  
import pyautogui  
import threading  

class TextPositionWindow:
    window_created = False  
    window_thread = None  
    window_root = None  
    window_text_box = None

    def __init__(self):
        # 初始化全局变量  
        self.window_created = False  
        self.window_thread = None
        self.window_root = None  
        self.window_text_box = None  

    def on_window_close(self):  
        # 退出Tkinter事件循环  
        self.window_root.quit()  

        # 清理全局变量  
        self.window_created = False  
        self.window_thread = None  
        self.window_root = None  
        self.window_text_box = None  

    def add_bullets_and_alternate_colors(self, string_list):  
        self.window_text_box.config(font=("黑体", 15))
        self.window_text_box.delete('1.0', tk.END)  # 清除文本框内容  
        for i, string in enumerate(string_list):  
            # 添加小圆点  
            bullet_string = "• " + string  
            
            # 设置背景色，交替使用两种颜色  
            if i % 2 == 0:  
                bg_color = "white"  # 偶数行背景色  
            else:  
                bg_color = "#bebebe"  # 奇数行背景色  
            
            # 插入带小圆点的字符串，并设置当前行的背景色  
            self.window_text_box.insert(tk.END, bullet_string + "\n\n", f"line{i}")
            self.window_text_box.tag_config(f"line{i}", background=bg_color)

    def update_window(self, string_list, x, y):
        # 更新窗口位置  
        self.window_root.geometry("+{}+{}".format(x, y))  
        
        # 添加文本框内容  
        self.add_bullets_and_alternate_colors(string_list)

        # 确保窗口在最顶层  
        self.window_root.attributes('-topmost', True) 
    
    def create_window(self, string_list, x, y):  
        # 创建新的Tkinter窗口  
        self.window_root = tk.Tk()  
        self.window_root.title("Mouse Position Window")  
        self.window_root.geometry("+{}+{}".format(x, y))  # 初始窗口位置  
        
        # 创建一个滚动文本框来显示字符串列表  
        self.window_text_box = scrolledtext.ScrolledText(self.window_root, wrap=tk.WORD)  
        self.window_text_box.pack(fill="both", expand=True)
        
        # 添加内容  
        self.add_bullets_and_alternate_colors(string_list)
        
        # 确保窗口在最顶层  
        self.window_root.attributes('-topmost', True) 
        
        # 绑定窗口关闭事件  
        self.window_root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # 显示窗口并进入事件循环  
        self.window_root.mainloop()  
    
    def create_window_at_mouse_position(self, string_list):        
        # 获取鼠标位置  
        x, y = pyautogui.position()  
        
        # 如果没有创建窗口或窗口线程已结束，则创建新窗口  
        if not self.window_created or not self.window_thread or not self.window_thread.is_alive():  
            self.window_thread = threading.Thread(target=self.create_window, args=(string_list, x - 100, y - 100))  
            self.window_thread.daemon = True  # 设置为守护线程  
            self.window_thread.start()  
            self.window_created = True  # 标记窗口已创建  
        else:  
            self.update_window(string_list, x - 100, y - 100)  # 更新已有窗口  

###### 全局变量 ######
ctrl_c_str = r"'\x03'"
ctrl_z_str = r"'\x1a'"
ctrl_x_str = r"'\x18'"
ctrl_o_str = r"'\x0f'"
ctrl_c_press_times = 0
ctrl_z_press_times = 0
ctrl_x_press_times = 0
ctrl_o_press_times = 0

exit_progress = False
hasSetting = False
setting = {}

transTextWindow = TextPositionWindow()
copyTextWindow = TextPositionWindow()

f = open("CaiYunXiaoYi.token")
CaiYunXiaoYiToken = f.read()

######################

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
    global exit_progress
    global ctrl_c_str, ctrl_c_press_times
    global ctrl_z_str, ctrl_z_press_times
    global ctrl_x_str, ctrl_x_press_times
    global ctrl_o_str, ctrl_o_press_times

    # print(key)
    if str(key) == ctrl_c_str:
        ctrl_c_press_times = ctrl_c_press_times + 1
    else:
        ctrl_c_press_times = 0

    if str(key) == ctrl_x_str:
        ctrl_x_press_times = ctrl_x_press_times + 1
    else:
        ctrl_x_press_times = 0

    if str(key) == ctrl_o_str or ctrl_c_press_times == 2:
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

        transTextWindow.create_window_at_mouse_position(tranlate_target)

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
    
    if ctrl_x_press_times == 2:
        copyTextWindow.create_window_at_mouse_position([])

    if str(key) == ctrl_z_str:
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