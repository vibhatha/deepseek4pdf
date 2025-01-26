"""Custom exceptions for PDF-LLM."""

class PDFLLMError(Exception):
    """Base exception for PDF-LLM."""
    pass

class PDFLoadError(PDFLLMError):
    """Raised when there's an error loading a PDF."""
    pass

class ModelConfigError(PDFLLMError):
    """Raised when there's an error configuring the LLM."""
    pass