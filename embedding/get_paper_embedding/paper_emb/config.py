import os
import json

basedir = os.path.dirname(__file__)

TFIDF_MODEL = os.path.join(basedir, 'corpus/tfidf_model.pkl')
SVD_MODEL = os.path.join(basedir, 'corpus/svd_model.pkl')
# md = os.getcwd()
# if md[-9:] == 'paper_emb':
#     TFIDF_MODEL = md + '/' + TFIDF_MODEL
#     SVD_MODEL = md + '/' + SVD_MODEL
# else:
#     TFIDF_MODEL = md + '/paper_emb/' + TFIDF_MODEL
#     SVD_MODEL = md + '/paper_emb/' + SVD_MODEL


fn_paper_text = os.path.join(basedir, 'corpus/pub_info.json')
fn_train = os.path.join(basedir, 'corpus/trainset.json')
fn_valid = os.path.join(basedir, 'corpus/validset.json')
fn_test = os.path.join(basedir, 'corpus/testset.json')
# md = os.getcwd()
# if md[-9:] == 'paper_emb':
#     fn_paper_text = md + '/' + fn_paper_text
#     fn_train = md + '/' + fn_train
#     fn_valid = md + '/' + fn_valid
#     fn_test = md + '/' + fn_test
# else:
#     fn_paper_text = md + '/paper_emb/' + fn_paper_text
#     fn_train = md + '/paper_emb/' + fn_train
#     fn_valid = md + '/paper_emb/' + fn_valid
#     fn_test = md + '/paper_emb/' + fn_test

recall_paper_text = '/data/zhuyifan/data/pub.json'
# load from http://10.10.0.38/aminer/pub.json
d2v_model_path = '/data/cache/aminer/d2v.model'
tfidf_model_path = '/data/cache/aminer/tfidf.model'
svd_model_path = '/data/cache/aminer/svd.model'
sbert_model_path = '/data/cache/aminer/sbert-model-en-256seq'
oagbert_model_path = 'D:/Develop/0411/rms_recall/embedding/saved/oagbert-v2-sim'
# C:\Users\nijzh\Desktop\saved\oagbert-v2-sim
# oagbert_model_path = 'C:/Users/nijzh/Desktop/saved/oagbert-v2-sim'