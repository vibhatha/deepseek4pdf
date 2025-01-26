"""pytest fixtures for deepseek4pdf tests."""

import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf():
    """Provide path to a sample PDF for testing."""
    return Path(__file__).parent / "data" / "sample.pdf"

@pytest.fixture
def pdf_engine():
    """Provide a configured PDFQueryEngine instance."""
    from deepseek4pdf import PDFQueryEngine
    return PDFQueryEngine()