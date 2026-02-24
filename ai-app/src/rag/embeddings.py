from langchain.embeddings import OpenAIEmbeddings

class CustomEmbeddings:
    def __init__(self, model_name="text-embedding-ada-002"):
        self.embeddings_model = OpenAIEmbeddings(model_name=model_name)

    def embed_text(self, text):
        return self.embeddings_model.embed(text)

    def embed_texts(self, texts):
        return self.embeddings_model.embed(texts)