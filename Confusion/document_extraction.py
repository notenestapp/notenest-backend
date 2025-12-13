import fitz
from docx.api import Document

def extract_pdf(path):
    doc = fitz.open(path)
    text = "".join([page.get_text() for page in doc])
    return text

def extract_docx(path_docx):
    document = Document(path_docx)
    all_texts = ""

    for p in document.paragraphs:
        all_texts += p.text
        all_texts += "\n"
    return all_texts


def main():
    path = "the-psychology-of-money-9780857197689-9780857197696_compress - Copy.pdf"
    print("Extracting from pdf")
    print(extract_pdf(path))
    print("Text extracted successfully")

    print("\nExtracting from docx")
    path_docx = "Test-docx.docx"
    print(extract_docx(path_docx))


if __name__ == "__main__":
    main()

