from pathlib import Path
import subprocess
import shutil
import os
import typer
import ollama
from rich.console import Console
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing_extensions import Annotated
import PyPDF2

TEMP_DIR = ".pdfchat"

console = Console()


def parse_pdf_to_md(path_to_pdf: str) -> str:
    """
    Convert a PDF file to Markdown format.
    :param path_to_pdf: Path to the PDF file.
    :return: Path to the converted Markdown file.
    """
    output_dir = TEMP_DIR
    subprocess.run(["marker_single", "--disable_image_extraction", "--output_dir", output_dir, path_to_pdf],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    file_name = Path(path_to_pdf).stem
    md_file_path = os.path.join(output_dir, file_name, f"{file_name}.md")
    return md_file_path


def init_chat_engine(path_to_md: str, model: str, ollama_base_url: str = "http://localhost:11434"):
    """Initialize the chat engine with the given PDF file and Ollama model."""
    documents = SimpleDirectoryReader(input_files=[path_to_md]).load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
    )
    chat_engine = index.as_chat_engine(
        llm=Ollama(model=model, request_timeout=1000.0, base_url=ollama_base_url),
        chat_mode="condense_plus_context",
    )
    return chat_engine


def is_user_exit_command(user_input: str) -> bool:
    """Check if the user input is a command to exit the chat."""
    return user_input.lower() in ["exit", "quit"]


def get_default_model() -> str:
    """
    Gets the first model from the list of installed models.
    If no models are installed, it prints an error message and exits.
    """
    models = [m['model'] for m in ollama.list().get('models', [])]
    if len(models) == 0:
        console.print("No models found. Please install a model using `ollama pull <model_name>`.")
        raise SystemExit(1)
    else:
        return models[0]


def validate_model_exists(model: str):
    """
    Validate if the specified model exists on device.
    If not, it prints an error message and exits.
    """
    try:
        ollama.show(model)
    except:
        console.print(f"Model '{model}' not found. Please install it using `ollama pull {model}`.")
        raise SystemExit(1)


def validate_pdf_file(path_to_pdf: str):
    if not os.path.exists(path_to_pdf):
        console.print(f"PDF file '{path_to_pdf}' not found.")
        raise SystemExit(1)
    if not path_to_pdf.endswith(".pdf"):
        console.print(f"File '{path_to_pdf}' is not a PDF file.")
        raise SystemExit(1)


def delete_temp_files():
    """Delete temporary files created during the chat session."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)


def chat(chat_engine):
    """
    Chat with the user using the chat engine.
    :param chat_engine: The chat engine initialized with the PDF file and model.
    :return: True if the user wants to continue chatting, False if they want to exit.
    """
    console.print("👤 [bold blue]User[/]: ", end="")
    user_input = input("")
    if is_user_exit_command(user_input):
        return False
    with console.status("[bold green]Processing...[/]") as status:
        streaming_response = chat_engine.stream_chat(user_input)
        for i, token in enumerate(streaming_response.response_gen):
            if i == 0:
                status.stop()
                console.print("🤖 [bold red]Model[/]: ", end="")
            console.print(token, end="")
    console.print()
    return True


def copy_selected_pdf_pages(path_to_pdf: str, pages: list[int]) -> str:
    """Copy selected PDF pages to a new file in TEMP directory."""
    reader = PyPDF2.PdfReader(path_to_pdf)
    writer = PyPDF2.PdfWriter()
    for page in pages:
        writer.add_page(reader.pages[page - 1])  # Page numbers are 0-indexed in PyPDF2
    output_pdf_path = os.path.join(TEMP_DIR, "selected_pages.pdf")
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)
    return output_pdf_path


def parse_pages_string_to_list(pages: str) -> list:
    """
    Parse a string of pages into a list of page numbers.
    :param pages: Comma-separated list of pages (e.g., "1,2,3" or "1-3" or mix of both).
    :return: List of page numbers.
    """
    page_numbers = set()
    for part in pages.split(","):
        if "-" in part:
            start, end = [int(x) for x in part.split("-")]
            page_numbers.update(range(start, end + 1))
        else:
            page_numbers.add(int(part))
    return sorted(page_numbers)

def init_temp_dir():
    """Initialize the temporary directory for storing PDF files."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

def app(path_to_pdf: Annotated[str, typer.Argument(help="Path to the PDF file.")],
        model: Annotated[str, typer.Option("--model", "-m",
                                           help="Ollama model to use (must be installed). "
                                                "Defaults to the first model returned by `ollama list`. (ex: llama3.1:8b)")] = None,
        ollama_base_url: Annotated[str, typer.Option("--url", "-u",
                                                     help="Ollama base URL. Defaults to 'http://localhost:11434'.")] = "http://localhost:11434",
        pages: Annotated[str, typer.Option("--pages", "-p",
                                           help="The pdf pages to parse. Defaults to all pages. Ex: 1,2,3 or 1-3 or 1-3,5-7.")] = None):
    """
    Run the PDF chat application.
    :param path_to_pdf: Path to the PDF file.
    :param model: Ollama model to use (must be installed).
    :param ollama_base_url: Ollama base URL. Defaults to 'http://localhost:11434'.
    :param pages: The PDF pages to parse. Defaults to all pages.
                  Ex: 1,2,3 or 1-3 or 1-3,5-7.
    """
    init_temp_dir()
    validate_pdf_file(path_to_pdf)
    if model is None:
        model = get_default_model()
    else:
        validate_model_exists(model)
    console.print(f"Using {model}")
    if pages is not None:
        pdf_pages = parse_pages_string_to_list(pages)
        path_to_pdf = copy_selected_pdf_pages(path_to_pdf, pdf_pages)
    with console.status(
            "[bold green]Parsing PDF...[/] (this may take a while if file is large or first time using pdfchat)"):
        path_to_md = parse_pdf_to_md(path_to_pdf)
    with console.status("[bold green]Starting chat engine..."):
        chat_engine = init_chat_engine(path_to_md, model, ollama_base_url=ollama_base_url)
    delete_temp_files()
    console.print("Chat engine initialized. You can now start chatting with the PDF.")
    console.print("Type 'exit' or 'quit' to stop the chat.")
    user_wants_to_continue = True
    while user_wants_to_continue:
        user_wants_to_continue = chat(chat_engine)


def run_app():
    typer.run(app)
