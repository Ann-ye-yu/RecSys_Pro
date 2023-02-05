from paper_emb.oag_tfidf_emb import get_oag_emb, get_tfidf_emb, get_oag_tfidf_emb
import json

if __name__ == '__main__':
    # Prepare a paper entity
    papers = json.load(open('./paper_emb/corpus/pub_info.json','r'))
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
    
    # get the embedding
    oag_emb = get_oag_emb(paper_example)
    idf_emb = get_tfidf_emb(paper_example)
    mix_emb = get_oag_tfidf_emb(paper_example)

    # shape
    print("OAG:{}|IDF:{}|MIX:{}".format(oag_emb.shape, idf_emb.shape, mix_emb.shape))