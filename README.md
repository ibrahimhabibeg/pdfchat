<h1 align="center">pdfchat</h1>

<p align="center">CLI app to quickly chat with your PDFs locally</p>

<p align="center">
  <a href="https://pypi.org/project/pdfchat/"><img src="https://img.shields.io/pypi/v/pdfchat?color=blue&label=PyPI&logo=pypi" alt="PyPI version"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
  <a href="https://github.com/ibrahimhabibeg/pdfchat"><img src="https://img.shields.io/badge/GitHub-Page-blue?logo=github" alt="GitHub Page"></a>
</p>

<hr/>

## Overview

`pdfchat` is a Python-based CLI app that utilizes open-source LLMs using Ollama to quickly open a chat session with a
PDF file. The app emphasizes speed as you can start chatting directly from the command line without needing to open a
GUI or web interface and security as it runs locally on your machine and your data is not sent to any external servers.

## Features

- Parse and extract content from PDF files.
- Chat with the content of the PDF using a conversational interface.
- Select specific pages of a PDF for focused interaction.
- Supports multiple language models via the Ollama platform.

## Use Cases

- **Students**: Quickly find information in textbooks or lecture notes. Have a tutor teach you content specific to your
  study material.
- **Researchers**: Extract data from research papers or articles. Ask questions about specific sections of a paper.
- **Educators**: Create interactive learning materials. Use the app to generate quizzes and questions based on the
  content of a PDF.
- **Business Professionals**: Review contracts, reports, or any other documents. Get clarifications on specific
  sections.
- **General Users**: Quickly find information in any PDF document. Reduce hallucinations by grounding the model with the
  content of the PDF.

## Installation

### Prerequisites

`pdfchat` assumes you have Ollama installed. If you haven't installed it yet, follow the instructions on
the [Ollama website](https://ollama.com/).
Make sure you have the required models installed. You can check the available models on
the [Ollama website](https://ollama.com/search).

You also need to have `marker-pdf` installed. You can install it using `pip`:

```bash
pip install marker-pdf
```

You can also install `marker-pdf` using `pipx`.

### Install `pdfchat`

To install `pdfchat` using `pipx`, run:

```bash
pipx install pdfchat
```

## Usage

### Basic Command

To start a chat session with a PDF file, run:

```bash
pdfchat <path_to_pdf>
```

Note: If it is your first time running the app, it will take a few seconds (depending on your internet speed) to
download PDF parsing and OCR models.

### Options

- `--model` or `-m`: Ollama model to use (must be installed). Defaults to the first model returned by `ollama list`. (
  ex: llama3.1:8b)
- `--url` or `-u`: Ollama base URL. Defaults to 'http://localhost:11434'
- `--pages` or `-p`: The pdf pages to parse. Defaults to all pages. Ex: 1,2,3 or 1-3 or 1-3,5-7. Defaults to all pages.

### Help

To see all available options, run:

```bash
pdfchat --help
```

This will display the help message with all available options and their descriptions.

### Example

```bash
pdfchat example.pdf --model llama3.1:8b
```

### Example

```bash
pdfchat example.pdf --model llama3.1:8b --pages 1-5
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

Developed by Ibrahim Habib. You can contact me through [LinkedIn](https://www.linkedin.com/in/ibrahimhabibeg/)
or [Email](mailto:ibrahimhabib.eg@gmail.com). 
