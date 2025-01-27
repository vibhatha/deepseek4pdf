"""Interactive terminal chat application for PDF documents."""

import argparse
import sys
from pathlib import Path
from typing import Optional
import readline  # Enables arrow key navigation and command history
from deepseek4pdf import PDFQueryEngine

class PDFChatApp:
    def __init__(self, pdf_path: Path):
        """Initialize the chat application."""
        self.engine = PDFQueryEngine()
        self.pdf_path = pdf_path
        self.chat_history: list[tuple[str, str]] = []
        
    def initialize(self):
        """Load the PDF and prepare the initial context."""
        print(f"Loading PDF: {self.pdf_path}")
        self.engine.load_pdf(self.pdf_path)
        print("PDF loaded successfully! You can start chatting.")
        print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.\n")

    def get_user_input(self) -> Optional[str]:
        """Get input from user with a prompt."""
        try:
            return input("\n🤔 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            return None

    def process_response(self, question: str):
        """Process and display the AI response."""
        print("\n🤖 Assistant: ", end="", flush=True)
        full_response = ""
        
        try:
            for chunk in self.engine.query(question):
                print(chunk, end="", flush=True)
                full_response += chunk
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return

        self.chat_history.append((question, full_response))
        print()  # New line after response

    def run(self):
        """Run the chat loop."""
        try:
            self.initialize()
            
            while True:
                user_input = self.get_user_input()
                
                if user_input is None or user_input.lower() in ['exit', 'quit']:
                    print("\nGoodbye! 👋")
                    break
                
                if not user_input:
                    continue
                
                self.process_response(user_input)
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
        except Exception as e:
            print(f"\n❌ Fatal Error: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Chat with a PDF document")
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the PDF file to chat about"
    )
    args = parser.parse_args()

    if not args.pdf_path.exists():
        print(f"Error: PDF file not found at {args.pdf_path}")
        sys.exit(1)

    app = PDFChatApp(args.pdf_path)
    app.run()

if __name__ == "__main__":
    main() 