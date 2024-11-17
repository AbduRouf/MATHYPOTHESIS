!pip install pix2text
p2t = Pix2Text.from_config()
from google.colab import drive
drive.mount('/content/drive')

import os
cur_path = '/content/drive/MyDrive/PDF_SUMMARY'

pdf_path = cur_path + "/pdf"
data_path = cur_path + "/data"
output_path = cur_path + "/output"

if not os.path.exists(data_path):
    os.mkdir(data_path)
from pix2text import set_logger, Pix2Text
from pix2text.layout_parser import ElementType
from PIL import Image
import string
import fitz
import sys
import os

# get one page image and return the output md file and all the titles, figures, tables on the page.
def get_page_content(page_img, page_num):
    titles = []
    figures = []
    page_output_path = output_path +'/' + str(page_num) + '/output-md'
    try:
        doc = p2t.recognize_page(page_img, table_as_image=True, text_contain_formula=False, save_debug_res=output_path + "/log") #, page_numbers=[0, 1])
        doc.to_markdown(page_output_path)  # The exported Markdown information is saved in the output-md directory

        for i, _ in enumerate(doc.elements):
            # pick out the title so that we could set up the questions for RAG
            if doc.elements[i].type == ElementType.TITLE:
                print("title:", doc.elements[i].text)
                titles.append(doc.elements[i].text)

    except Exception as e:
        print(e)

    return page_output_path, titles
# get the definition from pix2text/layout_parser.py

class ElementType(Enum):
    ABANDONED = -2
    IGNORED = -1
    UNKNOWN = 0
    TEXT = 1
    TITLE = 2
    FIGURE = 3
    TABLE = 4
    FORMULA = 5
def get_pdf_content(pdf_file):
    all_titles = []

    try:
        fitz.TOOLS.mupdf_warnings()  # empty the problem message container
        doc = fitz.open(pdf_file)
        warnings = fitz.TOOLS.mupdf_warnings()
        if warnings:
            print(warnings)
            raise RuntimeError()

        for i, page in enumerate(doc):  # iterate through the pages
            try:
                img = page.get_pixmap()  # render page to an image
                img_path = output_path + f"/{i}.png"
                img.save(img_path)  # store image as a PNG
                page_folder, titles = get_page_content(img_path, i)

                if titles:
                    all_titles.extend(titles)
            except:
                print("error when handling the image file {} -page {}".format(pdf_file, i))
                return None

        return all_titles

    except:
        print("error when opening the pdf file {}".format(pdf_file))
        return None
def parse_titles(title_list):
    caption = title_list[0]
    authors = title_list[1]
    sections ={}
    section_titles = ['I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'VII.', 'VIII.', 'IX.', 'X']
    subsection_titles = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.']
    cur_title =''

    for title in title_list[2:]:
        t = title.split()[0].strip()
        if t in section_titles:
            sections[title] = []
            cur_title = title
        elif t in subsection_titles:
            sections[cur_title].append(title)
    return sections
all_titles = get_pdf_content(cur_path + "/pdf/1901.00031v1.pdf")
display(parse_titles(all_titles))
