from sentence_transformers import SentenceTransformer
from .config import sbert_model_path


class SBERT_EMb():
    def __init__(self, model_path=sbert_model_path):
        self.model = SentenceTransformer(model_path)

    def get_emb(self, query):
        embedding = self.model.encode([query])
        return embedding