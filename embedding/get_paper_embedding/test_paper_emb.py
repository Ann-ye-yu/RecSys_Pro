import jsonlines
from paper_emb.doc2vec import Doc2vec_emb
from paper_emb.tfidf import TFIDF_Emb
from paper_emb.oagbert import OAG_BERT_Emb
from paper_emb.sentence_bert import SBERT_EMb
import numpy as np
from tqdm import tqdm
import argparse

paper_path = '/data/zhuyifan/data/pub.json'

def load_papers(paper_path):
    texts = list()
    with jsonlines.open(paper_path) as reader:
        for paper in reader:
            texts.append(paper["title"])
    print("{} papers loaded.".format(len(texts)))
    return texts

def load_paper_entity(paper_path):
    # used for oag-bert
    texts = list()
    with jsonlines.open(paper_path) as reader:
        for paper in reader:
            texts.append(paper)
    print("{} papers loaded.".format(len(texts)))
    return texts

def cosine_similarity(x,y):
    num = x.dot(y.T)
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    return num / denom

def find_similar_papers(querys, txts, model):
    query_emb = list()
    for each_query in querys:
        query_emb.append(model.get_emb(each_query))
    query_emb = np.array(query_emb)

    print("Embedding all paper titles.")
    title_emb = list()
    for each_title in tqdm(txts):
        title_emb.append(model.get_emb(each_title))
    title_emb = np.array(title_emb)
    
    for i, q in enumerate(query_emb):
        similarity = np.zeros((title_emb.shape[0]))
        for j, p in enumerate(tqdm(title_emb)):
            similarity[j] = cosine_similarity(title_emb[j], query_emb[i])
        similar_papers_id = (-similarity).argsort()[:10]
        print("[Topic]{}".format(querys[i]))
        for k, each_idx in enumerate(similar_papers_id):
            print("No.{}|{}".format(k,txts[each_idx]))

def find_similar_papers_oag(querys, txts, model):
    query_emb = list()
    #这里对于oag-bert输入的是一个字典，而不是一个字符串
    for each_query in querys:
        query_emb.append(model.get_emb({"title": each_query}))
    query_emb = np.array(query_emb)

    print("Embedding all paper with entities.")
    #这里对于oag-bert输入的是一个字典，而不是一个字符串
    title_emb = list()
    for each_paper in tqdm(txts):
        title_emb.append(model.get_emb(each_paper))
    title_emb = np.array(title_emb)
    
    for i, q in enumerate(query_emb):
        similarity = np.zeros((title_emb.shape[0]))
        for j, p in enumerate(tqdm(title_emb)):
            similarity[j] = p @ q.T # 这里计算相似度不用余弦距离，直接算向量点乘
        similar_papers_id = (-similarity).argsort()[:10]
        print("[Topic]{}".format(querys[i]))
        for k, each_idx in enumerate(similar_papers_id):
            print("No.{}|{}".format(k,txts[each_idx]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='lsa', help='Select a model from \{lsa, doc2vec, oag-bert, sentence-bert\}')
    args = parser.parse_args()

    #OAG需要加载实体，而其他的模型加载题目即可
    if args.model == 'oag-bert':
        txts = load_paper_entity(paper_path)
    else:
        txts = load_papers(paper_path)
    
    querys = [
        # "Knowledge Graph", 
        # "curriculum learning", 
        # "low permeability reservoir", 
        "social network",
        "machine learning",
        "Data Mining", 
        "GPT-3"
    ]
    if args.model == 'doc2vec':
        model = Doc2vec_emb()
        find_similar_papers(querys, txts, model)
    if args.model == 'sentence-bert':
        model = SBERT_EMb()
        find_similar_papers(querys, txts, model)
    elif args.model == 'oag-bert':
        model = OAG_BERT_Emb()
        find_similar_papers_oag(querys, txts, model)
    else:
        model = TFIDF_Emb()
        find_similar_papers(querys, txts, model)

