import importlib
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import time
import sys
from pdfminer.pdfpage import PDFPage


def pdf_parse_v2(filename):
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams

    laparmas = LAParams()
    laparmas.detect_vertical = False
    # laparmas.all_texts = True
    # laparmas.boxes_flow = 1
    # laparmas.line_overlap = 0.2
    # laparmas.char_margin = 10

    text = extract_text(filename, laparams=laparmas)
    text = text.split('\n')
    text = list(filter(lambda x: x != '', text))

    def full2half(s):
        n = ''
        for char in s:
            num = ord(char)
            if num == 0x3000:  # 将全角空格转成半角空格
                num = 32
            elif 0xFF01 <= num <= 0xFF5E:  # 将其余全角字符转成半角字符
                num -= 0xFEE0
            num = chr(num)
            n += num

        n = n.replace(' ', '')
        return n
    text = [full2half(i) for i in text]

    return text


importlib.reload(sys)
time1 = time.time()


def parse(filename):
    '''解析PDF文本，并保存到TXT文件中'''
    fp = open(filename, 'rb')
    # 用文件对象创建一个PDF文档分析器
    parser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument(parser)
    # 连接分析器，与文档对象
    parser.set_document(doc)

    # # 提供初始化密码，如果没有密码，就创建一个空的字符串
    # doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDF，资源管理器，来共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释其对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 循环遍历列表，每次处理一个page内容
        # doc.get_pages() 获取page列表
        pages = list(PDFPage.create_pages(doc))
        page = pages[0]

        interpreter.process_page(page)
        layout = device.get_result()
        return layout

        # for page in pages:
        #     interpreter.process_page(page)
        #     # 接受该页面的LTPage对象
        #     layout = device.get_result()
        #     # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
        #     # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
        #     # 想要获取文本就获得对象的text属性，
        #     # for x in layout:
        #     #     if (isinstance(x, LTTextBoxHorizontal)):
        #     #         with open(TXT_path, 'a') as f:
        #     #             results = x.get_text()
        #     #             f.write(results + "\n")


if __name__ == '__main__':
    filename = '.temp/pdf/normal.pdf'
    layout = parse(filename)
