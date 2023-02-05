from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from .config import tfidf_model_path, svd_model_path, recall_paper_text
import os
import joblib
import jsonlines
from tqdm import tqdm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer


class TFIDF_Emb():
    def __init__(self, model_path=tfidf_model_path, svd_path=svd_model_path, text_path=recall_paper_text):
        if os.path.exists(model_path) and  os.path.exists(svd_path):
            self.model_path = model_path
            self.svd_path = svd_path
            self.text_path = text_path
            self.vectorizer = joblib.load(self.model_path)
            self.svd = joblib.load(self.svd_path)
            self.normalizer = Normalizer(copy=False)
            self.lsa = make_pipeline(self.svd, self.normalizer)
        else:
            self.model_path = model_path
            self.svd_path = svd_path
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
            
        # documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(texts)]
        self.vectorizer = TfidfVectorizer(
                max_df=0.5,
                max_features=10000,
                min_df=2,
                stop_words="english",
                use_idf=True,
            )
        # fname = get_tmpfile("my_doc2vec_model")
        X = self.vectorizer.fit_transform(texts)
        self.svd = TruncatedSVD(n_components=100, n_iter=5, random_state=42, tol=1e-8)
        
        self.normalizer = Normalizer(copy=False)
        self.lsa = make_pipeline(self.svd, self.normalizer)
        X = self.lsa.fit_transform(X)

        joblib.dump(self.vectorizer, self.model_path)
        joblib.dump(self.svd, self.svd_path)

        print("model training done.")

    def finetune(self, texts_new):
        #事实上是重新训练模型，不是微调
        print("model retrain...")
        texts = list()

        for paper in tqdm(texts_new):
            texts.append(paper.lower())
            
        # documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(texts)]
        self.vectorizer = TfidfVectorizer(
                max_df=0.5,
                max_features=10000,
                min_df=2,
                stop_words="english",
                use_idf=True,
            )
        # fname = get_tmpfile("my_doc2vec_model")
        X = self.vectorizer.fit_transform(texts)
        self.svd = TruncatedSVD(n_components=100, n_iter=5, random_state=42, tol=1e-8)
        
        self.normalizer = Normalizer(copy=False)
        self.lsa = make_pipeline(self.svd, self.normalizer)
        X = self.lsa.fit_transform(X)

        joblib.dump(self.vectorizer, self.model_path)
        joblib.dump(self.svd, self.svd_path)

        print("model training done.")
    
    def get_emb(self, query):
        tf_idf_emb = self.vectorizer.transform([query.lower()])
        tf_idf_emb_zip = self.lsa.transform(tf_idf_emb)
        return tf_idf_emb_zip