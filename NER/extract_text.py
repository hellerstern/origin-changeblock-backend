import argparse
import pdfplumber
import re
# import module
from pdf2image import convert_from_path
from pytesseract import pytesseract
# from configs import PATH_TESSERACT
import docx


# ----------------------------------------------------------------------
def check_is_table_row(text):
    if len(re.split(r'\s{2,}', text)) >= 3:
        return True
    return False


# ----------------------------------------------------------------------
def preprocess_page(lst_text, include_tables):
    lst_text_final = []
    num_4dots = 0
    for text in lst_text:
        text = text.strip()
        # check if the page is table of content
        if text.lower() == 'table of contents' or text.lower() == 'contents':
            return []
        if '.....' in text:
            num_4dots += 1
            if num_4dots == 3:
                return []
        if not text:
            continue
        if not include_tables:
            if check_is_table_row(text):
                continue
        lst_text_final.append(text)

    return lst_text_final


# ----------------------------------------------------------------------
def remove_header(lst_page):
    try:
        page_1 = lst_page[3]
        page_2 = lst_page[4]
        page_3 = lst_page[5]
        header = ''
        # print(page_1[0],page_2[0],page_3[0])
        if page_1[0] == page_2[0] and page_1[0] == page_3[0]:
            header = page_1[0]

            lst_page = [page[1:] for page in lst_page if page[0] == header]

        return lst_page
    except:
        return lst_page


# ----------------------------------------------------------------------
def get_first_number_from_right(text: str) -> int:
    for i in range(len(text)-1, -1, -1):
        if text[i].isdigit():
            return int(text[i])
    return None


# ----------------------------------------------------------------------
def remove_page_number(lst_page):
    # import ipdb;ipdb.set_trace()
    try:
        page_1 = lst_page[3]
        page_2 = lst_page[4]
        page_3 = lst_page[5]

        x1 = get_first_number_from_right(page_1[-1])
        x2 = get_first_number_from_right(page_2[-1])
        x3 = get_first_number_from_right(page_3[-1])

        if x1+1 == x2 and x2+1 == x3:
            lst_page = [page[:-1] for page in lst_page]
            # print(lst_page[0][:-1])
    except:
        pass

    return lst_page


# ----------------------------------------------------------------------
def curves_to_edges(cs):
    edges = []
    for c in cs:
        edges += pdfplumber.utils.rect_to_edges(c)
    return edges


# ----------------------------------------------------------------------
# def not_within_bboxes(obj):
#     """Check if the object is in any of the table's bbox."""
#     def obj_in_bbox(_bbox):
#         v_mid = (obj["top"] + obj["bottom"]) / 2
#         h_mid = (obj["x0"] + obj["x1"]) / 2
#         x0, top, x1, bottom = _bbox
#         return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
#     return not any(obj_in_bbox(__bbox) for __bbox in bboxes)


# ----------------------------------------------------------------------
def extract_pdf(pdf_path, include_tables=False):

    def not_within_bboxes(obj):
        def obj_in_bbox(_bbox):
            v_mid = (obj["top"] + obj["bottom"]) / 2
            h_mid = (obj["x0"] + obj["x1"]) / 2
            x0, top, x1, bottom = _bbox
            return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
        return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

    pdf = pdfplumber.open(pdf_path)

    # Load the first page.
    documents = []
    # tqdm.tqdm.write("Processing PDF...")
    for p in pdf.pages:
        if not include_tables:
            ts = {
                "vertical_strategy": "explicit",
                "horizontal_strategy": "explicit",
                "explicit_vertical_lines": curves_to_edges(p.curves + p.edges),
                "explicit_horizontal_lines": curves_to_edges(p.curves + p.edges),
                "intersection_y_tolerance": 10,
            }
            try:
                bboxes = [table.bbox for table in p.find_tables(
                    table_settings=ts)]

                lst_text = p.filter(
                    not_within_bboxes).extract_text().split('\n')
            except:
                lst_text = p.extract_text().split('\n')
        else:
            lst_text = p.extract_text().split('\n')

        lst_text = preprocess_page(lst_text, include_tables=include_tables)
        if len(lst_text) > 0:
            documents.append(lst_text)

    documents = remove_header(documents)
    documents = remove_page_number(documents)
    documents_ = ['\n'.join(page) for page in documents]
    documents__ = '\n'.join(documents_)

    return documents__


# ----------------------------------------------------------------------

def extract_docx(path: str) -> str:
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


# ----------------------------------------------------------------------
def is_pdf_full_image(pdf_path):
    # Open the PDF file using PyPDF2
    pdf = pdfplumber.open(pdf_path)

    # print(len(pdf.pages))
    for p in pdf.pages:
        if len(p.extract_text().strip()) != 0:
            return False
        # print(p.extract_text())

    return True


# ----------------------------------------------------------------------
def extract_text_from_img(img):
    # path_to_tesseract = PATH_TESSERACT
    # pytesseract.tesseract_cmd = path_to_tesseract
    text = pytesseract.image_to_string(img)
    # print(text)
    # with open("text.txt", "a") as text_file:
    #     text_file.write(text)
    return text


# ----------------------------------------------------------------------
def extract_text_from_pdf_images(pdf_path):
    # images = convert_from_path('pdf/Midshore_Flare_Issuance_Deed_4-27-15.pdf')
    images = convert_from_path(pdf_path)
    documents = []
    for i in range(len(images)):
        text = extract_text_from_img(images[i])
        lst_text = text.split('\n')
        lst_text = preprocess_page(lst_text, include_tables=False)
        if len(lst_text) > 0:
            documents.append(lst_text)
    # import ipdb; ipdb.set_trace()
    documents = remove_header(documents)
    documents = remove_page_number(documents)
    documents_ = ['\n'.join(page) for page in documents]
    documents__ = '\n'.join(documents_)

    return documents__
# ----------------------------------------------------------------------


def extract_text(path: str, include_tables=False) -> str:
    if path.endswith('.pdf') or path.endswith('.PDF'):
        # print("PDF")
        if is_pdf_full_image(path):
            # print("PDF is full image")
            return extract_text_from_pdf_images(path)
        return extract_pdf(path, include_tables=include_tables)
    elif path.endswith('.docx') or path.endswith('.doc') or path.endswith('.DOCX') or path.endswith('.DOC'):
        # print("DOCX")
        return extract_docx(path)
    else:
        raise Exception("File format not supported")
