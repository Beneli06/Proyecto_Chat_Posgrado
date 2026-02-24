import pytest
from src.pdf_processing.parser import parse_pdf
from src.pdf_processing.extractor import extract_text

def test_parse_pdf_valid_file():
    result = parse_pdf('tests/sample.pdf')
    assert result is not None
    assert isinstance(result, dict)
    assert 'text' in result
    assert 'metadata' in result

def test_parse_pdf_invalid_file():
    with pytest.raises(FileNotFoundError):
        parse_pdf('tests/non_existent.pdf')

def test_extract_text_valid_content():
    sample_content = "This is a sample PDF content."
    result = extract_text(sample_content)
    assert result == "This is a sample PDF content."

def test_extract_text_empty_content():
    sample_content = ""
    result = extract_text(sample_content)
    assert result == ""