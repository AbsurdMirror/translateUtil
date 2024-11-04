import pdfplumber  
import threading  
import queue  
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from trans_core import tranlateText
from PyPDF2 import PdfReader, PdfWriter  
from reportlab.lib.pagesizes import letter  
from reportlab.pdfgen import canvas  
import io  

def add_text_to_pdf(text_to_add, pdf_path):  
    writer = PdfWriter()  

    # 读取现有的 PDF 文件  
    import os
    if os.path.exists(pdf_path):  
        reader = PdfReader(pdf_path)  
        for page in reader.pages:  
            writer.add_page(page)  

    # 创建一个新的 PDF 页面并添加字符串  
    packet = io.BytesIO()  
    can = canvas.Canvas(packet, pagesize=letter)  
    can.drawString(100, 750, text_to_add)  # 设置文本位置和文本内容  
    can.save()  
  
    # 将内存中的 PDF 数据移到起始位置  
    packet.seek(0)  
  
    # 创建一个新的 PdfReader 对象来读取新创建的 PDF 页面  
    new_pdf_reader = PdfReader(packet)  
  
    # 将新页面添加到 writer 中  
    writer.add_page(new_pdf_reader.pages[0])  
  
    # 将最终的 PDF 写入文件  
    with open(pdf_path, 'wb') as output_pdf_file:  
        writer.write(output_pdf_file)  
  
def extract_text_from_pdf(pdf_path, text_queue):  
    """  
    从PDF文件中提取文字，并将结果放入队列中  
    """  
    print(f"开始从PDF {pdf_path} 中提取文字...")  
    text = ""  
    with pdfplumber.open(pdf_path) as pdf:  
        for page in pdf.pages:  
            print(f"提取第{page.page_number}页的文字。")  
            text = page.extract_text()  
            text_queue.put(text)  
    print(f"提取完成。")  

def translate_text(text_queue, translated_queue, trans_func):  
    """  
    从队列中读取文字，进行翻译，并将结果放入另一个队列中  
    """  
    print("开始翻译文字...")  
    i= 0
    while True:  
        text = text_queue.get()  
        if text is None:  # 使用None作为结束信号  
            break  
        translated_text = trans_func(text)  
        print(f"翻译第{ i + 1} 页的文字。")  
        i += 1
        translated_queue.put(translated_text)  
    print("翻译完成。")  

def save_translated_text(translated_queue, output_dir_path):  
    """  
    从队列中读取翻译后的文字，并保存到文件中  
    """  
    i = 0
    while True:  
        translated_text = translated_queue.get()  
        if translated_text is None:  # 使用None作为结束信号  
            break       
        print(f"开始保存翻译后的文字到 {output_dir_path}/page_{i}.txt...")  
        with open(f"{output_dir_path}/page_{i}.txt", "w", encoding="utf-8") as file:  
            print(f"保存第{i}页的文字。")
            file.write(translated_text)  
            # add_text_to_pdf(translated_text, output_dir_path)
            i += 1
    print(f"保存完成")  
  
def main(pdf_path, trans_func, output_dir_path):  
    text_queue = queue.Queue()  
    translated_queue = queue.Queue()  
  
    # 创建并启动线程  
    extractor_thread = threading.Thread(target=extract_text_from_pdf, args=(pdf_path, text_queue))  
    translator_thread = threading.Thread(target=translate_text, args=(text_queue, translated_queue, trans_func))  
    saver_thread = threading.Thread(target=save_translated_text, args=(translated_queue, output_dir_path))  
  
    extractor_thread.start()  
    translator_thread.start()  
    saver_thread.start()  
  
    # 等待提取线程完成  
    extractor_thread.join()  
  
    # 向翻译线程发送结束信号  
    text_queue.put(None)  

    # 等待翻译线程完成
    translator_thread.join()  

    # 向保存线程发送结束信号
    translated_queue.put(None)  

    # 等待保存线程完成
    saver_thread.join()  
  
if __name__ == "__main__":  
    pdf_path = "C:/Users/dongzhengxiang/Downloads/IHI0022E_amba_axi_and_ace_protocol_spec-315-328.pdf"  # 替换为你的PDF文件路径  
    output_dir_path = "tran_pdf_out"
    main(pdf_path, tranlateText, output_dir_path) # trans)
