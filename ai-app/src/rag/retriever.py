from typing import List, Dict
import numpy as np

class Retriever:
    def __init__(self, embeddings_model):
        self.embeddings_model = embeddings_model

    def retrieve(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, float]]:
        query_embedding = self.embeddings_model.encode(query)
        document_embeddings = self.embeddings_model.encode(documents)

        similarities = np.dot(document_embeddings, query_embedding.T)
        top_k_indices = similarities.argsort()[-top_k:][::-1]

        results = [{"document": documents[i], "similarity": similarities[i]} for i in top_k_indices]
        return results