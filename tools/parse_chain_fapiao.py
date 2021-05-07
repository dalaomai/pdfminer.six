import os
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer import layout as pdfminer_layout
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from pdfminer.pdfpage import PDFPage


class Word:

    def __init__(self, x0, y0, x1, y1, text) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text


class Line:
    def __init__(self, x0, y0, x1, y1) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Extractor(object):
    INVOICE_ELEMENTS = {
        'CODE': '发票代码',
        'NUMBER': '发票号码',
        'DATE': '开票日期',
        'CHECK_CODE': '校 验 码',
    }

    def __init__(self, path):
        self.file = path if os.path.isfile else None
        self.layout = None
        self.words = []
        self.lines = []
        self.curves = []

        self.vertical_lines = []
        self.horizontal_lines = []
        self.points = []

    def _load_data(self):
        fp = open(self.file, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        parser.set_document(doc)
        if not doc.is_extractable:
            raise Exception('pdf not etractable')

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = list(PDFPage.create_pages(doc))
        page = pages[0]

        interpreter.process_page(page)
        self.layout = device.get_result()
        for x in self.layout:
            x.y0, x.y1 = x.y1, x.y0
            x.y0 = self.layout.height - x.y0
            x.y1 = self.layout.height - x.y1

            if isinstance(x, pdfminer_layout.LTTextBox):
                # text = x.get_text()
                # text = text.replace('\n\n', '').strip('\n')
                # self.words.append(Word(x.x0, x.y0, x.x1, x.y1, text))

                texts = x.get_text().replace('\n\n', '').strip('\n').split('\n')
                texts_len = len(texts)
                average_hight = x.height / texts_len

                for index, text in enumerate(texts, start=0):
                    self.words.append(
                        Word(
                            x.x0,
                            x.y0 + average_hight * index,
                            x.x1,
                            x.y0 + average_hight * (index+1),
                            text
                        )
                    )

            elif isinstance(x, pdfminer_layout.LTLine):
                self.lines.append(
                    Line(
                        x.x0,
                        x.y0,
                        x.x1,
                        x.y1
                    )
                )
            elif isinstance(x, pdfminer_layout.LTCurve):
                self.curves.append(x)

    def _calute_point(self):
        for line in self.lines:
            if line.x0 == line.x1:
                self.vertical_lines.append(line)
            elif line.y0 == line.y1:
                self.horizontal_lines.append(line)
            else:
                raise Exception(
                    f"不是一条线：{line.x0};{line.x1}:{line.y0}:{line.y1}")
        for curve in self.curves:
            self.vertical_lines.append(
                Line(curve.x0, curve.y0, curve.x0, curve.y1)
            )
            self.vertical_lines.append(
                Line(curve.x1, curve.y0, curve.x1, curve.y1)
            )
            self.horizontal_lines.append(
                Line(curve.x0, curve.y0, curve.x1, curve.y0)
            )
            self.horizontal_lines.append(
                Line(curve.x0, curve.y1, curve.x1, curve.y1)
            )

        delta = 1
        for vline in self.vertical_lines:
            for hline in self.horizontal_lines:
                if (
                    hline.x0-delta <= vline.x0 <= hline.x1+delta and
                    vline.y0-delta <= hline.y0 <= vline.y1+delta
                ):
                    self.points.append(
                        Point(
                            vline.x0, hline.y0
                        )
                    )

    def draw_image(self):
        import cv2
        import matplotlib.pyplot as plt
        import numpy as np
        from PIL import ImageFont, ImageDraw, Image

        green = (0, 255, 0)
        red = (0, 0, 255)
        yellow = (255, 0, 0)
        colorful = (100, 100, 100)

        fontpath = 'cmaprsrc/simsun.ttc'
        font = ImageFont.truetype(fontpath, 8)

        mat1 = np.zeros(
            (
                int(self.layout.height), int(self.layout.width), 3
            ),
            dtype="uint8"
        )

        for line in self.lines:
            cv2.line(
                mat1,
                (int(line.x0), int(line.y0)),
                (int(line.x1), int(line.y1)),
                green, 1
            )

        for word in self.words:
            cv2.rectangle(
                mat1,
                (int(word.x0), int(word.y0)),
                (int(word.x1), int(word.y1)),
                red, 1
            )

        img_pil = Image.fromarray(mat1)
        draw = ImageDraw.Draw(img_pil)
        for word in self.words:
            text = word.text
            draw.text(
                (int(word.x0), int(word.y0)),
                text,
                font=font,
                fill=green
            )
        mat1 = np.array(img_pil)

        for curve in self.curves:
            cv2.rectangle(
                mat1,
                (int(curve.x0), int(curve.y0)),
                (int(curve.x1), int(curve.y1)),
                yellow, 1
            )

        for point in self.points:
            cv2.circle(
                mat1,
                (int(point.x), int(point.y)),
                5, colorful, 3
            )

        plt.figure()
        plt.title("lines")
        plt.imsave(".temp/lines.png", mat1)

    def find_invoice_element(self):
        y_min = min(self.points, key=lambda x: x.y).y
        useful_words = list(filter(lambda x: x.y1 < y_min, self.words))
        result = {}

        for element_k, element_v in self.INVOICE_ELEMENTS.items():
            element_words = filter(
                lambda x: x.text.find(element_v) != -1, useful_words)

            for element_word in element_words:
                def is_target(useful_word):
                    center_point = Point(
                        (useful_word.x1+useful_word.x0)/2,
                        (useful_word.y1+useful_word.y0)/2
                    )
                    return (
                        center_point.x > element_word.x1 and
                        element_word.y0 < center_point.y < element_word.y1
                    )

                target_words = filter(
                    lambda x: is_target(x),
                    useful_words
                )
                for target_word in target_words:
                    result[element_k] = target_word.text

        return result


if __name__ == "__main__":
    path = r'.temp/pdf/normal.pdf'
    extractor = Extractor(path=path)
    extractor._load_data()
    extractor._calute_point()
    print(extractor.find_invoice_element())
    extractor.draw_image()
