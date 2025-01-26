from typing import Generator, Optional
from pathlib import Path
import tempfile

from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class PDFQueryEngine:
    """A class to handle PDF document querying using LLM."""
    
    def __init__(
        self,
        llm_model: str = "deepseek-r1:1.5b",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        request_timeout: float = 120.0
    ):
        """Initialize the PDF Query Engine.
        
        Args:
            llm_model: Name of the Ollama model to use
            embedding_model: Name of the HuggingFace embedding model
            request_timeout: Timeout for LLM requests in seconds
        """
        self._temp_dir = None
        self._query_engine = None
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.request_timeout = request_timeout
        
    def load_pdf(self, pdf_path: str | Path) -> None:
        """Load a PDF file into the query engine.
        
        Args:
            pdf_path: Path to the PDF file
        """
        # Create temporary directory if not exists
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp()
            
        # Copy PDF to temp directory
        pdf_path = Path(pdf_path)
        dest_path = Path(self._temp_dir) / pdf_path.name
        dest_path.write_bytes(pdf_path.read_bytes())
        
        self._setup_query_engine()
        
    def _setup_query_engine(self) -> None:
        """Setup the LlamaIndex query engine with models and prompt template."""
        # Setup LLM
        llm = Ollama(
            model=self.llm_model,
            request_timeout=self.request_timeout
        )
        
        # Setup embedding model
        embed_model = HuggingFaceEmbedding(
            model_name=self.embedding_model,
            trust_remote_code=True
        )
        
        # Configure settings
        Settings.embed_model = embed_model
        Settings.llm = llm

        # Load documents
        loader = SimpleDirectoryReader(
            input_dir=self._temp_dir,
            required_exts=[".pdf"],
            recursive=True
        )
        docs = loader.load_data()

        # Create index and query engine
        index = VectorStoreIndex.from_documents(docs, show_progress=True)
        
        # Setup streaming query engine with custom prompt
        qa_prompt_tmpl_str = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information above I want you to think step by step "
            "to answer the query in a crisp manner, incase case you don't know "
            "the answer say 'I don't know!'.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
        
        self._query_engine = index.as_query_engine(streaming=True)
        self._query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
        )

    def query(self, question: str) -> Generator[str, None, None]:
        """Query the loaded PDF documents.
        
        Args:
            question: The question to ask about the PDF content
            
        Yields:
            Chunks of the answer as they are generated
            
        Raises:
            RuntimeError: If no PDF has been loaded
        """
        if not self._query_engine:
            raise RuntimeError("No PDF loaded. Call load_pdf() first.")
            
        response = self._query_engine.query(question)
        
        for chunk in response.response_gen:
            yield chunk