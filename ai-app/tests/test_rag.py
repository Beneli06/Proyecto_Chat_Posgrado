from src.rag.retriever import Retriever
from src.rag.embeddings import Embeddings

def test_retriever_initialization():
    retriever = Retriever()
    assert retriever is not None

def test_embeddings_initialization():
    embeddings = Embeddings()
    assert embeddings is not None

def test_retriever_functionality():
    retriever = Retriever()
    result = retriever.retrieve("sample query")
    assert isinstance(result, list)  # Assuming retrieve returns a list

def test_embeddings_functionality():
    embeddings = Embeddings()
    vector = embeddings.embed("sample text")
    assert len(vector) > 0  # Assuming embed returns a non-empty vector