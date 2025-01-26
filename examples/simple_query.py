"""Example usage of deepseek4pdf."""

from deepseek4pdf import PDFQueryEngine

def main():
    # Initialize the engine
    engine = PDFQueryEngine()
    
    # Load a PDF
    engine.load_pdf("data/sample_gzt.pdf")
    
    # Query the PDF
    question = "What are the main topics discussed in the document?"
    for chunk in engine.query(question):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    main()