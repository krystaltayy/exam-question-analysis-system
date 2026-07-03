
import re
from docx import Document
import PyPDF2


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())

    return "\n".join(text)


def extract_text_from_pdf(file_path):
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def split_questions(text):
    questions = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            questions.append(line)

    return questions