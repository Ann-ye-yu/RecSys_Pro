from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import joblib
from .tfidf_pretrain import pretain_LSA
import os
import numpy as np
try:
    from cogdl.oag import oagbert
except:
    from cogdl import oagbert
import torch
import json
import torch.nn.functional as F
from .config import TFIDF_MODEL,SVD_MODEL

# TF-IDF
if os.path.exists(TFIDF_MODEL):
    vectorizer = joblib.load(TFIDF_MODEL)
    svd = joblib.load(SVD_MODEL)
else:
    vectorizer, svd = pretain_LSA(TFIDF_MODEL, SVD_MODEL)

# OAG-BERT
tokenizer, bert_model = oagbert("oagbert-v2-sim")

def get_oag_emb(input_dict):
    title = input_dict['title']
    if 'abstract' in input_dict:
        abstract = input_dict['abstract']
    else:
        abstract = ''
    if 'keywords' in input_dict:
        concepts = input_dict['keywords']
    else:
        concepts = []
    if 'venue' in input_dict:
        venue = input_dict['venue']
    else:
        venue = ''
    # authors and affiliations are lists.
    if 'authors' in input_dict:
        authors = input_dict['authors']
    else:
        authors = []
    if 'affiliations' in input_dict:
        affiliations = input_dict['affiliations']
    else:
        affiliations = []
    # build model inputs
    # print("Paper Info:\n{}\n{}\n{}\n{}\n{}\n{}".format(title,abstract,venue,authors,concepts,affiliations))
    input_ids, input_masks, token_type_ids, masked_lm_labels, position_ids, position_ids_second, masked_positions, num_spans = bert_model.build_inputs(
        title=title, abstract=abstract, venue=venue, authors=authors, concepts=concepts, affiliations=affiliations
    )
    # run forward
    sequence_output, pooled_output = bert_model.bert.forward(
        input_ids=torch.LongTensor(input_ids).unsqueeze(0),
        token_type_ids=torch.LongTensor(token_type_ids).unsqueeze(0),
        attention_mask=torch.LongTensor(input_masks).unsqueeze(0),
        output_all_encoded_layers=False,
        checkpoint_activations=False,
        position_ids=torch.LongTensor(position_ids).unsqueeze(0),
        position_ids_second=torch.LongTensor(position_ids).unsqueeze(0)
    )
    del abstract
    del concepts
    del venue
    del authors
    del affiliations
    del input_ids
    del input_masks
    del token_type_ids
    del masked_lm_labels
    del position_ids
    del position_ids_second
    del masked_positions
    del num_spans
    del sequence_output
    pooled_output = F.normalize(pooled_output, p=2, dim=1)
    emb = pooled_output.detach().numpy().astype('float32').flatten()
    del pooled_output
    return emb

def get_tfidf_emb(input_dict):
    text = input_dict['title']
    if text[-1] != '.':
        text += '.'
    if 'abstract' in input_dict:
        text += input_dict['abstract']
    tf_idf_emb = vectorizer.transform([text])
    tf_idf_emb_zip = svd.transform(tf_idf_emb)
    del tf_idf_emb
    del text
    return tf_idf_emb_zip.reshape(-1)

def get_oag_tfidf_emb(input_dict):
    tf_idf_emb = get_tfidf_emb(input_dict)
    oag_emb = get_oag_emb(input_dict)
    return np.append(tf_idf_emb, oag_emb)


if __name__ == '__main__':
    papers = json.load(open('./corpus/pub_info.json','r'))
    paper_example = papers[list(papers.keys())[0]]
    if 'keywords_more' in paper_example and ('keywords' not in paper_example or len(paper_example['keywords'])) == 0:
        paper_example['keywords'] = [each_key for each_key in paper_example['keywords_more'].keys()]
    if 'authors' in paper_example:
        authors = []
        affiliations = []
        for each_author in paper_example['authors']:
            if 'name' in each_author:
                authors.append(each_author['name'])
            if 'org' in each_author:
                affiliations.append(each_author['org'])
        paper_example['authors'] = authors
        paper_example['affiliations'] = affiliations
        
    oag_emb = get_oag_emb(paper_example)
    idf_emb = get_tfidf_emb(paper_example)
    mix_emb = get_oag_tfidf_emb(paper_example)
    print("InOAG:{}|IDF:{}|MIX:{}".format(oag_emb.shape, idf_emb.shape, mix_emb.shape))