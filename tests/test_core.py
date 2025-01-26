import pytest
from pathlib import Path
import tempfile
from deepseek4pdf.core import PDFQueryEngine

@pytest.fixture
def sample_pdf():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        # Write some dummy PDF content
        tmp.write(b"%PDF-1.4\nSample PDF content")
        pdf_path = Path(tmp.name)
    yield pdf_path
    pdf_path.unlink()  # Cleanup after tests

@pytest.fixture
def query_engine():
    """Create a PDFQueryEngine instance."""
    return PDFQueryEngine()

def test_init_default_values():
    """Test initialization with default values."""
    engine = PDFQueryEngine()
    assert engine.llm_model == "deepseek-r1:1.5b"
    assert engine.embedding_model == "BAAI/bge-large-en-v1.5"
    assert engine.request_timeout == 120.0

def test_init_custom_values():
    """Test initialization with custom values."""
    engine = PDFQueryEngine(
        llm_model="custom-model",
        embedding_model="custom-embedding",
        request_timeout=60.0
    )
    assert engine.llm_model == "custom-model"
    assert engine.embedding_model == "custom-embedding"
    assert engine.request_timeout == 60.0

def test_load_pdf(query_engine, sample_pdf):
    """Test loading a PDF file."""
    query_engine.load_pdf(sample_pdf)
    assert query_engine._temp_dir is not None
    assert query_engine._query_engine is not None

def test_query_without_pdf(query_engine):
    """Test querying without loading a PDF first."""
    with pytest.raises(RuntimeError, match="No PDF loaded"):
        next(query_engine.query("What is in the PDF?"))

@pytest.mark.integration
def test_query_with_pdf(query_engine, sample_pdf):
    """Test querying with a loaded PDF."""
    query_engine.load_pdf(sample_pdf)
    response = query_engine.query("What is in the PDF?")
    # Test that we can get at least one response chunk
    assert next(response, None) is not None
