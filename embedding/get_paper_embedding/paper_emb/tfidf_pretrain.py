from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import joblib
import json
import os
import numpy as np
from tqdm import tqdm
from .config import fn_paper_text, fn_train, fn_valid, fn_test


def pretain_LSA(tfidf_model_filename, svd_mode_filename):
    print('Using LSA to pretrain language for initial run.')
    paper_to_idx = {}
    corpus = []
    paper_info = json.load(open(fn_paper_text,'r'))
    file_names = [fn_train, fn_valid, fn_test]
    count = 0
    for each_filename in file_names:
        print(each_filename)
        records = json.load(open(each_filename,'r'))
        print(len(records))
        for each_user in tqdm(records):
            for each_record in each_user:
                if each_record['item'] not in paper_to_idx:
                    if each_record['item'] in paper_info:
                        text = paper_info[each_record['item']]['title']
                        if text[-1] != '.':
                            text += '.'
                        if 'abstract' in paper_info[each_record['item']]:
                            text += paper_info[each_record['item']]['abstract']
                        paper_to_idx[each_record['item']] = count
                        corpus.append(text)
                        count += 1
    print('Paper loaded, start training...')
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    print('Training finished.')
    print(X.shape)
    svd = TruncatedSVD(n_components=100, n_iter=7, random_state=42)
    X = svd.fit_transform(X)
    print('LSA process finished.')
    joblib.dump(vectorizer, tfidf_model_filename)
    joblib.dump(svd, svd_mode_filename)
    return vectorizer, svd
