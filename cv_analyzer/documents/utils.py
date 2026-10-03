import pymupdf
from typing import Union
from django.db.models.fields.files import FieldFile


def extract_text_from_pdf(file: Union[FieldFile, str]) -> str:
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