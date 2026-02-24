"""
RAG Query Engine - Handles retrieval and response generation
"""

import os
import logging
from typing import Optional, List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

logger = logging.getLogger(__name__)

# System prompt to prevent hallucinations
SYSTEM_PROMPT = """Eres un asistente experto en programas de posgrado de la Universidad. 
Tu rol es proporcionar información precisa, ética y amable a los aspirantes.

INSTRUCCIONES CRÍTICAS:
1. SOLO responde preguntas basadas en la documentación oficial de la Universidad.
2. Si la información no se encuentra en los documentos disponibles, di explícitamente: 
   "No tengo información disponible sobre esto. Te recomiendo contactar directamente a la oficina de posgrados."
3. NUNCA inventes, especules o asumos información que no esté en los documentos.
4. Sé siempre respetuoso, profesional y empático con los aspirantes.
5. Proporciona respuestas claras, estructuradas y concisas.

CONTEXTO DE LA DOCUMENTACIÓN:
{context}

PREGUNTA DEL USUARIO:
{question}
"""


class RAGQueryEngine:
    """
    Handles RAG (Retrieval-Augmented Generation) queries.
    
    Process:
    1. Receive user query
    2. Retrieve relevant documents from vector database
    3. Build prompt with retrieved context
    4. Generate response using LLM
    """
    
    def __init__(
        self,
        vector_db_path: str = "./chroma_db",
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: int = 1000,
        retrieval_k: int = 5
    ):
        """
        Initialize the RAG query engine.
        
        Args:
            vector_db_path: Path to the vector database
            model_name: LLM model to use (gpt-4, gpt-3.5-turbo)
            temperature: Temperature for response generation (0.0-1.0)
            max_tokens: Maximum tokens in response
            retrieval_k: Number of documents to retrieve
        """
        self.vector_db_path = vector_db_path
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.retrieval_k = retrieval_k
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize vector store
        self.vector_store = None
        self._init_vector_store()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _init_vector_store(self):
        """Initialize connection to vector database."""
        try:
            self.vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info("Connected to vector database")
        except Exception as e:
            logger.error(f"Failed to connect to vector database: {str(e)}")
            self.vector_store = None
    
    def _retrieve_context(self, query: str) -> str:
        """
        Retrieve relevant documents from vector database.
        
        Args:
            query: User query
            
        Returns:
            str: Concatenated context from retrieved documents
        """
        if self.vector_store is None:
            logger.warning("Vector store not initialized")
            return ""
        
        try:
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(
                query,
                k=self.retrieval_k
            )
            
            # Concatenate document contents
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            logger.info(f"Retrieved {len(docs)} documents for query")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return ""
    
    def query(
        self,
        question: str,
        return_sources: bool = True
    ) -> dict:
        """
        Process a user query and generate a response.
        
        Args:
            question: User's question
            return_sources: Whether to return source documents
            
        Returns:
            dict: Response data including answer and sources
        """
        if not question or not isinstance(question, str):
            return {
                "success": False,
                "error": "Invalid question format",
                "answer": None,
                "sources": []
            }
        
        try:
            # Retrieve context
            context = self._retrieve_context(question)
            
            if not context:
                return {
                    "success": False,
                    "error": "No relevant documents found in the database",
                    "answer": "Lo sentimos, no encontramos información relevante en nuestra base de datos. Por favor, contacta a la oficina de posgrados.",
                    "sources": []
                }
            
            # Build prompt
            prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
            
            # Create chain
            chain = (
                {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
                | prompt
                | self.llm
            )
            
            # Generate response
            response = chain.invoke({
                "context": context,
                "question": question
            })
            
            # Retrieve source documents
            sources = []
            if return_sources and self.vector_store:
                docs = self.vector_store.similarity_search(question, k=self.retrieval_k)
                sources = [
                    {
                        "content": doc.page_content[:200],
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", 0)
                    }
                    for doc in docs
                ]
            
            return {
                "success": True,
                "answer": response.content,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "answer": None,
                "sources": []
            }
