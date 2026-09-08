import pymupdf

def extract_text_from_pdf(file) -> str:
    """
    Extracts raw text from an uploaded PDF file.
    """
    # Django's FieldFile has a .path attribute with the absolute path
    if hasattr(file, 'path'):
        file_path = file.path
    else:
        file_path = file

    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text