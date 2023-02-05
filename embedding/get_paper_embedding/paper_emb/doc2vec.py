from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile
from .config import recall_paper_text, d2v_model_path
import jsonlines
from tqdm import tqdm
import os

class Doc2vec_emb():
    def __init__(self, model_path=d2v_model_path, text_path=recall_paper_text):
        if os.path.exists(model_path):
            self.model_path = model_path
            self.text_path = text_path
            self.model = Doc2Vec.load(self.model_path)  # you can continue training with the loaded model!
        else:
            self.model_path = model_path
            self.text_path = text_path
            self.init_model()

    def init_model(self):
        print("model init...")
        texts = list()
        with jsonlines.open(self.text_path) as reader:
            for paper in tqdm(reader):
                texts.append(paper["title"].lower())
                texts.append(paper["abstract"].lower())
                # if "keywords" in paper:
                    # for each_word in paper["keywords"]:
                    #     texts.append(each_word)
            
        documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(texts)]
        self.model = Doc2Vec(documents, vector_size=300, window=5, min_count=5, workers=8)
        # fname = get_tmpfile("my_doc2vec_model")
        self.model.save(self.model_path)
        print("model training done.")
    
    def finetune(self, texts):
        documents = [TaggedDocument(doc.lower(), [i]) for i, doc in enumerate(texts)]
        self.model.train(documents)
        self.model.save(self.model_path)
        print("finetune done.")
    
    def get_emb(self, query):
        vector = self.model.infer_vector([query.lower()])
        return vector



