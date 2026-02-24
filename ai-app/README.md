# AI Application README

# AI Application

This project is a postgraduate AI application that utilizes FastAPI or Flask for the backend. It implements a Retrieval-Augmented Generation (RAG) logic, processes PDF files, and includes unit tests to ensure the functionality of the application.

## Project Structure

```
ai-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── config.py              # Configuration settings
│   ├── api
│   │   ├── __init__.py        # Initializes the API package
│   │   └── routes.py          # Defines the API routes
│   ├── rag
│   │   ├── __init__.py        # Initializes the RAG package
│   │   ├── retriever.py       # Logic for retrieving relevant data
│   │   └── embeddings.py      # Handles embeddings for RAG
│   ├── pdf_processing
│   │   ├── __init__.py        # Initializes the PDF processing package
│   │   ├── parser.py          # Parses PDF files
│   │   └── extractor.py       # Extracts text and metadata from PDFs
│   └── utils
│       ├── __init__.py        # Initializes the utils package
│       └── helpers.py         # Utility functions
├── tests
│   ├── __init__.py            # Initializes the tests package
│   ├── test_api.py            # Unit tests for API routes
│   ├── test_rag.py            # Unit tests for RAG logic
│   ├── test_pdf_processing.py  # Unit tests for PDF processing
│   └── test_utils.py          # Unit tests for utility functions
├── requirements.txt            # Lists project dependencies
├── pytest.ini                  # Configuration for pytest
└── README.md                   # Project documentation
```

## Features

- **RAG Logic**: Implements retrieval-augmented generation to enhance responses based on user queries.
- **PDF Processing**: Capable of parsing and extracting information from PDF files.
- **Unit Testing**: Comprehensive tests to ensure the reliability of the application components.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ai-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file as needed.

## Running the Application

To start the application, run:
```
python src/main.py
```

## Running Tests

To execute the tests, use:
```
pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.