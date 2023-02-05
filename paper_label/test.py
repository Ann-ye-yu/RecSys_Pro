import json

from oagbert import OAG_BERT_Emb

oag_bert_model = OAG_BERT_Emb()
with open("corpus/pub.json", 'r', encoding="utf-8") as f:
    j = 0
    for line in f:
        j = j + 1
        if j == 494:
            paper = json.loads(line)
            print(paper)
            paper_keys = paper.keys()
            for key in paper_keys:
                value = paper[key]
                if isinstance(value, str) and value == None:
                    paper[key] = ""
                elif isinstance(value, list):
                    for i in range(len(value)):
                        if value[i] == None:
                            del value[i]
            print(paper)



# print(text)
# text = {"tags": [], "ts": "2021-01-01 14:00:03", "_id": "5feefcf491e0113b2659ff1c",
#         "title": "Bridging Cost-sensitive and Neyman-Pearson Paradigms for Asymmetric  Binary Classification",
#         "abstract": "  Asymmetric binary classification problems, in which the type I and II errors have unequal severity, are ubiquitous in real-world applications. To handle such asymmetry, researchers have developed the cost-sensitive and Neyman-Pearson paradigms for training classifiers to control the more severe type of classification error, say the type I error. The cost-sensitive paradigm is widely used and has straightforward implementations that do not require sample splitting; however, it demands an explicit specification of the costs of the type I and II errors, and an open question is what specification can guarantee a high-probability control on the population type I error. In contrast, the Neyman-Pearson paradigm can train classifiers to achieve a high-probability control of the population type I error, but it relies on sample splitting that reduces the effective training sample size. Since the two paradigms have complementary strengths, it is reasonable to combine their strengths for classifier construction. In this work, we for the first time study the methodological connections between the two paradigms, and we develop the TUBE-CS algorithm to bridge the two paradigms from the perspective of controlling the population type I error. ",
#         "keywords": [], "venue": "Arxiv", "authors": ["Jingyi Jessica Li"], "affiliations": [null]}

papers_embedding = oag_bert_model.get_emb(paper)
print(papers_embedding.shape)
