from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def extract_metadata_from_pdf(pdf_path):
    metadata = {}
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            metadata = reader.metadata
    except Exception as e:
        print(f"Error extracting metadata from {pdf_path}: {e}")
    return metadata