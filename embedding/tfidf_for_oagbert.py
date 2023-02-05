import json
import pickle
import re,os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from embedding.config import *
import spacy
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.decomposition import TruncatedSVD


STOPWORDS_EN = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
                'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
                'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
                'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn',
                'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'}


class TfidfGenerator:
    """
    1. 每次init时加载模型
    2. 生成时微调一下
    3. 保存
    """

    def __init__(self):
        # 1. load tfidf-200.
        self.tfidf_transform = pickle.load(open(TF_IDF_PATH, 'rb'))
        self.count_vec = CountVectorizer(decode_error='replace', vocabulary=pickle.load(open(FEATURES_PATH, 'rb')))
        self.svd = pickle.load(open(SVD_PATH, 'rb'))
        self.nlp = spacy.load('en_core_web_sm')
        self.lemmatizer = self.nlp.get_pipe('lemmatizer')

    def content_filter(self, sentence: str):
        temp = re.sub(r"\$.*?\$", "", sentence)
        # 2.1. remove special characters
        temp = re.sub("[^A-Za-z0-9\'\s]", " ", temp)
        temp = re.sub('[a-zA-Z]+://[^\s]*[.com|.cn]', '', temp)  # remove url
        # 2.2. remove continuous spaces
        temp = re.sub("\s+", ' ', temp)
        # 2.3. convert text to words' origin type.
        doc = self.nlp(temp)
        # 2.3. remove stopwords.
        words_list = [token.lemma_ for token in doc]
        cleaned_words_list = list()
        for word in words_list:
            word = word.lower()  #
            if word.isdigit() or len(word) <= 2 or word in STOPWORDS_EN:  # remove digit.
                continue
            cleaned_words_list.append(word)
        return " ".join(cleaned_words_list)

    def generate_idf_vector(self, paper: dict):
        sentence = list()
        # 1. prepare raw inputs.
        sentence.append(paper['title'])
        if 'abstract' in paper:
            sentence.append(paper['abstract'])
        if 'keywords' in paper and type(paper['keywords']) is list:
            sentence.append(" ".join(paper['keywords']))
        # 2. filter.
        # 2.0. remove mathematical formulas.
        cleaned_sentence = self.content_filter(" ".join(sentence))
        idf_emb = self.tfidf_transform.transform(self.count_vec.transform([cleaned_sentence]))
        return self.svd.transform(idf_emb)

    # def pre_train(self):
    #     path = './corpus/filter.json'
    #     with open(path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #
    #     vectorizer = CountVectorizer(decode_error='replace')
    #     transformer = TfidfTransformer()
    #
    #     vec_train = vectorizer.fit_transform(data)
    #     tfidf = transformer.fit_transform(vec_train)
    #
    #     with open('tfidf-200/feature.pkl', 'wb') as f:
    #         pickle.dump(vectorizer.vocabulary_, f)
    #
    #     with open('tfidf-200/tfidf.pkl', 'wb') as f:
    #         pickle.dump(transformer, f)
    #
    #     svd = TruncatedSVD(n_components=200).fit(tfidf)
    #     with open('tfidf-200/svd.p', 'wb') as f:
    #         pickle.dump(svd, f)


if __name__ == '__main__':
    """
     title = input_dict['title']
        if 'abstract' in input_dict:
            abstract = input_dict['abstract']
        else:
            abstract = ''
        if 'keywords' in input_dict:
            concepts = input_dict['keywords']
        else:
            concepts = []
    """
    generator = TfidfGenerator()

    paper = {
        "title": "Expression of the hedgehog signaling pathway and the effect of inhibition at the level of Smoothened in canine osteosarcoma cell lines.",
        "keywords": [],
        "abstract": "Osteosarcoma (OSA) is the most common malignant bone cancer in dogs. Canine and human OSA share several features, including tumor environments, response to traditional treatment, and several molecular pathways. Hedgehog (Hh) signaling is known to contribute to tumorigenesis and progression of various cancers, including human OSA. This study aimed to identify the role of the Hh signaling pathway in canine OSA cell lines, including Abrams, D17, and Moresco, focusing on the signal transducer Smoothened (SMO). mRNA and protein levels of Hh pathway components, including SHH, IHH, SMO, and PTCH1, were aberrant in all examined OSA cell lines compared with canine osteoblast cells. The SMO inhibitor cyclopamine significantly decreased cell viability and colony-forming ability in the canine OSA cell lines in a dose-dependent manner. Moresco cells, which expressed the highest level of SMO protein, were the most sensitive to the anticancer effect of cyclopamine among the three canine OSA cell lines tested. Hh downstream target gene and protein expression in canine OSA cell lines were downregulated after cyclopamine treatment. In addition, cyclopamine significantly increased apoptotic cell death in Abrams and Moresco cells. The findings that Hh/SMO is activated in canine OSA cell lines and cyclopamine suppresses OSA cell survival via inhibition of SMO suggest that the Hh/SMO signaling pathway might be a novel therapeutic target for canine OSA. This article is protected by copyright. All rights reserved.",
    }
    # generator.pre_train()
    emb = generator.generate_idf_vector(paper=paper)
    print(len(emb[0]))