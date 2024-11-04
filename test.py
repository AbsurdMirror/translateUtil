from PyPDF2 import PdfReader, PdfWriter  
from reportlab.lib.pagesizes import letter  
from reportlab.pdfgen import canvas  
import io  
  
def add_text_to_pdf(pdf_path, text_to_add):  
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
  
# 使用示例  
pdf_path = 'output.pdf'  
text_to_add = 'This is the text added to the end of the PDF.\nThis is the text added to the end of the PDF.\nThis is the text added to the end of the PDF.\nThis is the text added to the end of the PDF.\nThis is the text added to the end of the PDF.\n'  
add_text_to_pdf(pdf_path, text_to_add)