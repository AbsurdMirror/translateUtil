from pynput.keyboard import Controller, Key, Listener 
import pyperclip
import os  
import tkinter as tk  
from tkinter import scrolledtext  
import pyautogui  
import threading  
from bs4 import BeautifulSoup  
import webbrowser 
import re
import sys

# 添加模块路径到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_group_sentences')))

from trans_core import *
from ai_group_sentences.api_selector import group_sentences_to_paragraphs


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

transTextWindow = None
copyTextWindow = None

print("update NLTK ...")  
nltk_update()
print("update NLTK finish.")
print("欢迎使用 Translate Tool")


######################

###### 翻译功能 ######
# 解析函数
def parse_paragraphs(input_string):
    paragraphs = []
    pattern = r"\[(\d+):(\d+)\]\s*<([^>]+)>"
    for line in input_string.strip().split("\n"):
        match = re.search(pattern, line)
        if match:
            start, end, summary = match.groups()
            # 转换为零索引形式
            start = int(start) + 1
            end = int(end) + 1
            paragraphs.append([(start, end), summary])
    return paragraphs

def tranlateMain(source_content):
    no_newline_content, tranlate_source = split_string_by_english_sentences(source_content)
    # tranlate_target = []
    tranlate_target = tranlateCaiYunXiaoYi(tranlate_source, "auto2zh")
    tranlate_source_formatted = json.dumps(tranlate_source, indent=4, ensure_ascii=False)
    tranlate_target_formatted = json.dumps(tranlate_target, indent=4, ensure_ascii=False)  

    os.system('cls')
    print(f"剪切板内容: {source_content} \n")
    print(f"去除换行: {no_newline_content} \n")
    print(f"句子拆分: {tranlate_source_formatted} \n")
    print(f"翻译结果: {tranlate_target_formatted} \n")

    paragraphs = None
    if hasSetting:
        if setting["useAI"]:
            numbered_lines = [f"{index}: {line}" for index, line in enumerate(tranlate_target)]
            numbered_lines = "\n".join(numbered_lines)
            resp_text = group_sentences_to_paragraphs(numbered_lines, setting["ai_model"])
            print(f"AI段落拆分: \n{resp_text} \n")
            paragraphs = parse_paragraphs(resp_text)

    tranlate_source_target = []
    i = 0
    for item in tranlate_source:
        tranlate_source_target.append(item + "\n" + tranlate_target[i])
        i = i + 1

    tranlate_show = []
    if hasSetting:
        if setting["show"]["showSource"]:
            tranlate_show = tranlate_source_target
        else:
            tranlate_show = tranlate_target

    if paragraphs is None:
        paragraphs = [[(1, len(tranlate_show)), "翻译结果"]]

    transTextWindow.create_window_at_mouse_position(tranlate_show, paragraphs)

    if hasSetting :
        if setting["save"]["isSave"]:
            fileDirpath = os.path.join("./save", setting["save"]["savePath"])
            if not os.path.exists(fileDirpath):  
                os.makedirs(fileDirpath)
            filePath = os.path.join(fileDirpath, setting["save"]["saveName"])

            tranlate_save = []
            if setting["save"]["saveSource"]:
                tranlate_save = tranlate_source_target
            else:
                tranlate_save = tranlate_target

            with open(filePath, "a", encoding="utf-8") as savefile:
                for item in tranlate_save:
                    # 将每一项写入文件，并在每一项后添加一个换行符  
                    savefile.write(item + '\n')
                    if setting["save"]["saveSource"]:
                        savefile.write('\n')
                savefile.write("\n\n---\n---\n\n")

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
        tranlateMain(clipboard_content)
        ctrl_c_press_times = 0
    
    if ctrl_x_press_times == 2:
        copyTextWindow.create_window_at_mouse_position()

    if str(key) == ctrl_z_str:
        # 结束程序
        print("End program")
        listener.stop()
        exit_progress = True
  
def on_release(key):  
    global ctrl_pressed  
    if key == Key.ctrl:  
        ctrl_pressed = 0  
######################

###### UI界面 ######
class TextPositionWindow:
    window_created = False  
    window_thread = None  
    window_root = None  
    window_text_box = None
    window_side_text = None
    paned_window = None
    right_frame = None
    detail_web_url = "https://dict.cn/"

    def __init__(self):
        # 初始化全局变量  
        self.window_created = False  
        self.window_thread = None
        self.window_root = None  
        self.window_text_box = None  
        self.window_side_text = None

    def on_window_close(self):  
        # 退出Tkinter事件循环  
        self.window_root.quit()  

        # 清理全局变量  
        self.window_created = False  
        self.window_thread = None  
        self.window_root = None  
        self.window_text_box = None  
        self.window_side_text = None

    def add_bullets_and_alternate_colors(self, string_list, summary, group_index):         
        if group_index == 0:
            self.group_ranges = {}
            self.window_text_box.config(font=("微软雅黑", 13))
            self.window_text_box.delete('1.0', tk.END)  # 清除文本框内容  
            
            self.window_side_text.config(font=("微软雅黑", 12))
            self.window_side_text.delete('1.0', tk.END)  # 清除文本框内容  

        # 插入段落总结，并设置标签
        summary_tag = f"group{group_index}_summary"
        self.window_text_box.insert(tk.END, summary + "\n\n", summary_tag)
        self.window_text_box.tag_config(summary_tag, background="#F0F0AA", foreground="#333333", selectbackground="pink")
        
        # 绑定点击事件到段落总结
        self.window_text_box.tag_bind(summary_tag, "<Button-1>", 
                                    lambda event, idx=group_index: self.toggle_group_lines(idx))

        start_index = self.window_text_box.index("end-1c").split(".")[0]  # 当前插入点的起始行号
        for i, string in enumerate(string_list):  
            # 添加小圆点  
            bullet_string = "• " + string  
            
            # 设置背景色，交替使用两种颜色  
            if i % 2 == 0:  
                bg_color = "#F0F0F0"  # 偶数行背景色  
            else:  
                bg_color = "#E0EAF1"  # 奇数行背景色  
            
            # 插入带小圆点的字符串，并设置当前行的背景色  
            self.window_text_box.insert(tk.END, bullet_string + "\n\n", f"group{group_index}_line{i}")
            self.window_text_box.tag_config(f"group{group_index}_line{i}", background=bg_color, foreground="#333333", selectbackground="pink")

        end_index = self.window_text_box.index("end-1c").split(".")[0]  # 当前插入点的结束行号
        self.group_ranges[group_index] = (int(start_index), int(end_index))  # 记录段落的行范围

    def toggle_group_lines(self, group_index):
        """
        折叠或展开指定段落的内容。
        """
        if not hasattr(self, "group_ranges"):
            self.group_ranges = {}  # 初始化段落范围记录字典
        
        # 获取段落的行范围
        start_line, end_line = self.group_ranges.get(group_index, (None, None))
        if start_line is None or end_line is None:
            return  # 如果没有记录范围，则直接返回
        
        # 检查段落内容是否已隐藏
        hidden = self.is_group_hidden(group_index)
        
        if hidden:
            # 如果已隐藏，则重新显示内容
            for line in range(start_line, end_line):
                self.window_text_box.tag_configure(f"group{group_index}_line{line - start_line}", elide=False)
        else:
            # 如果未隐藏，则隐藏内容
            for line in range(start_line, end_line):
                self.window_text_box.tag_configure(f"group{group_index}_line{line - start_line}", elide=True)
        
        # 更新隐藏状态
        self.set_group_hidden(group_index, not hidden)


    def is_group_hidden(self, group_index):
        """
        检查指定段落的内容是否已被隐藏。
        """
        if not hasattr(self, "_hidden_groups"):
            self._hidden_groups = {}  # 初始化隐藏状态字典
        return self._hidden_groups.get(group_index, False)


    def set_group_hidden(self, group_index, hidden):
        """
        设置指定段落的隐藏状态。
        """
        if not hasattr(self, "_hidden_groups"):
            self._hidden_groups = {}  # 初始化隐藏状态字典
        self._hidden_groups[group_index] = hidden

    def on_right_click(self,event):  
        # 获取self.window_text_box选中内容的单词  
        word_start = self.window_text_box.index("sel.first")
        word_end = self.window_text_box.index("sel.last")

        before_string = self.window_text_box.get('1.0', word_start)
        sentence_start_index = before_string.rfind('\n')
        if sentence_start_index == -1:
            sentence_start_index = 0
        sentence_before = before_string[sentence_start_index:]

        after_string = self.window_text_box.get(word_end, tk.END)
        sentence_end_index = after_string.find('\n')
        if sentence_end_index == -1:
            sentence_end_index = len(after_string)
        sentence_after = after_string[:sentence_end_index]

        selected_word = self.window_text_box.get(word_start, word_end)
        sentence = sentence_before + selected_word + sentence_after
        print(sentence)

        if selected_word:  # 如果找到了单词  
            self.window_side_text.config(font=("微软雅黑", 12))
            self.window_side_text.delete('1.0', tk.END)  # 清除文本框内容  
            self.window_side_text.insert(tk.END, "获取中……")
            self.window_side_text.update()
  
            # 查找选中单词的词性  
            tagged_words = pos_tag(word_tokenize(sentence))  
            for word, pos in tagged_words:  
                if word.lower() == selected_word.lower():  
                    word_pos = pos  
                    break  
            else:  
                word_pos = None  
                      
            # 词形还原  
            lemmatizer = WordNetLemmatizer()  
            if not word_pos:
                reduced_word = selected_word  # 无法确定词性时，保持原样  
            elif word_pos.startswith('J'):  # 形容词  
                reduced_word = lemmatizer.lemmatize(selected_word, pos='a')  
            elif word_pos.startswith('V'):  # 动词  
                reduced_word = lemmatizer.lemmatize(selected_word, pos='v')  
            elif word_pos.startswith('N'):  # 名词  
                reduced_word = lemmatizer.lemmatize(selected_word, pos='n')  
            elif word_pos.startswith('R'):  # 副词  
                reduced_word = lemmatizer.lemmatize(selected_word, pos='r')  
            else:  
                reduced_word = selected_word  # 无法确定词性时，保持原样  

            # 发送GET请求
            url = "https://apii.dict.cn/mini.php?q=" + reduced_word
            response = requests.get(url)  
            self.detail_web_url = url
            self.window_side_text.delete('1.0', tk.END)  # 清除文本框内容  

            # print(tagged_words, selected_word, reduced_word)
            # print(url, response.text)
  
            # 检查请求是否成功  
            if response.status_code == 200:  
                soup = BeautifulSoup(response.text, 'lxml')  
                trans_text = soup.text
                trans_text = trans_text.replace("\n", " ")  
                trans_text = trans_text.replace("[", "\n[")  
                trans_text = trans_text.replace("]", "]\n")  
                trans_text = trans_text.replace("Define ", "\nDefine \n\n")  
                trans_text = trans_text.replace("例句与用法", "\n\n例句与用法")  
                pattern = r'(\d+)(\.|\s)'  # \d+ 匹配一个或多个数字，\. 匹配点号  
                replacement = r'\n\g<1>\g<2>'  # \g<1> 引用第一个括号中匹配的内容  
                trans_text = re.sub(pattern, replacement, trans_text)  
                self.window_side_text.insert(tk.END, trans_text)  
            else:  
                self.window_side_text.insert(tk.END, f"请求失败，状态码：{response.status_code}")  

    def open_web(self):
        webbrowser.open(self.detail_web_url)

    def update_window(self, string_list, paragraphs, x, y):
        # 更新窗口位置  
        self.window_root.geometry("+{}+{}".format(x, y))  
        
        # 添加新的段落
        for i, ((start, end), summary) in enumerate(paragraphs):
            paragraph_sentences = string_list[start - 1:end]
            self.add_bullets_and_alternate_colors(paragraph_sentences, summary, i)

        # 确保窗口在最顶层  
        self.window_root.attributes('-topmost', True) 
    
    def create_window(self, string_list, paragraphs, x, y):  
        # 创建新的Tkinter窗口  
        self.window_root = tk.Tk()  
        self.window_root.title("Mouse Position Window")  
        self.window_root.geometry("+{}+{}".format(x, y))  # 初始窗口位置  

        # 使用Panedwindow来分割左右两个区域  
        self.paned_window = tk.PanedWindow(self.window_root, orient=tk.HORIZONTAL)  
        self.paned_window.pack(fill=tk.BOTH, expand=True)  

        # 创建一个滚动文本框来显示字符串列表  
        self.window_text_box = scrolledtext.ScrolledText(self.window_root, wrap=tk.WORD)  
        self.window_text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 填充并扩展至左侧 

        # 将滚动文本框添加到panedwindow的左侧  
        self.paned_window.add(self.window_text_box)  

        # 绑定双击事件  
        self.window_text_box.tag_bind("sel", "<Button-3>", self.on_right_click)  
        
        # 右侧的框架，包含小文本框和按钮  
        self.right_frame = tk.Frame(self.paned_window)  
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  

        # 创建小侧边滚动文本框  
        self.window_side_text = scrolledtext.ScrolledText(self.right_frame, height=5, width=30)
        self.window_side_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)  # 仅垂直填充右侧 

        # 创建按钮，并绑定open_web函数到按钮的点击事件  
        web_button = tk.Button(self.right_frame, text="详细翻译", command=self.open_web)  
        web_button.pack(side=tk.BOTTOM, fill=tk.X, pady=5)  # 将按钮放置在窗口右上角 

        # 将右侧框架添加到panedwindow的右侧  
        self.paned_window.add(self.right_frame)  

        # 添加内容  
        for i, ((start, end), summary) in enumerate(paragraphs):
            paragraph_sentences = string_list[start - 1:end]
            self.add_bullets_and_alternate_colors(paragraph_sentences, summary, i)

        # 确保窗口在最顶层  
        self.window_root.attributes('-topmost', True) 
        
        # 绑定窗口关闭事件  
        self.window_root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # 显示窗口并进入事件循环  
        self.window_root.mainloop()  
    
    def create_window_at_mouse_position(self, string_list, paragraphs):        
        # 获取鼠标位置  
        x, y = pyautogui.position()  
        
        # 如果没有创建窗口或窗口线程已结束，则创建新窗口  
        if not self.window_created or not self.window_thread or not self.window_thread.is_alive():  
            self.window_thread = threading.Thread(target=self.create_window, args=(string_list, paragraphs, x - 100, y - 100))  
            self.window_thread.daemon = True  # 设置为守护线程  
            self.window_thread.start()  
            self.window_created = True  # 标记窗口已创建  
        else:  
            self.update_window(string_list, paragraphs, x - 100, y - 100)  # 更新已有窗口  

class CopyTextPositionWindow:
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

    def copy_translate_text(self):  
        # 获取文本框中的内容  
        text = self.window_text_box.get("1.0", tk.END)  
        # 将内容复制到剪贴板  
        tranlateMain(text)

    def update_window(self, string_list, x, y):
        # 更新窗口位置  
        self.window_root.geometry("+{}+{}".format(x, y))  

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
        
        # 创建按钮，并绑定copy_text函数到按钮的点击事件  
        copy_button = tk.Button(self.window_root, text="翻译文本", command=self.copy_translate_text)  
        copy_button.pack(side=tk.RIGHT, anchor=tk.N)  # 将按钮放置在窗口右上角 
        
        # 确保窗口在最顶层  
        self.window_root.attributes('-topmost', True) 
        
        # 绑定窗口关闭事件  
        self.window_root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # 显示窗口并进入事件循环  
        self.window_root.mainloop()  
    
    def create_window_at_mouse_position(self):        
        # 获取鼠标位置  
        x, y = pyautogui.position()  
        
        # 如果没有创建窗口或窗口线程已结束，则创建新窗口  
        if not self.window_created or not self.window_thread or not self.window_thread.is_alive():  
            self.window_thread = threading.Thread(target=self.create_window, args=([], x - 100, y - 100))  
            self.window_thread.daemon = True  # 设置为守护线程  
            self.window_thread.start()  
            self.window_created = True  # 标记窗口已创建  
        else:  
            self.update_window([], x - 100, y - 100)  # 更新已有窗口  

transTextWindow = TextPositionWindow()
copyTextWindow = CopyTextPositionWindow()
######################

###### 读取配置 ######
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
######################

# 使用with语句来确保Listener正确关闭  
with Listener(on_press=on_press, on_release=on_release) as listener:  
    listener.join()

while(not exit_progress) :
    a = 1