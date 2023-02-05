# Get Paper Embedding

A simple toolbox for getting a representation vector of a paper, and a toolbox for recommending paper to users.

## Requirements and installation 
Requirements:
* Python version >= 3.6
* PyTorch version >= 1.6.0
* Network for initial run

We also use the following packages, which you may install via `pip install -r requirements.txt`.
* tqdm
* scikit-learn
* joblib
* numpy
* torch
* cogdl
* pandas
* scipy
* sparsesvd
* jsonlines

Alternatively, please install [sentence-transformers](https://www.sbert.net/) if you want to use sentenceBERT.

## Functions and Directory

Currently this repo consists of two parts, which are `paper_emb` and `CF_recommendation`.
`paper_emb` is a simple toolbox for getting a representation vector of a paper, while `CF_recommendation` is used for recommending paper to users.
Their codes are organized in two independant folders, which can work separately.

## Usage of Get Embedding of a Paper (NEW!)

First of all, modify `/paper_emb/config.py`, and edit the path of data and models.
```python
# paper data, may load from http://10.10.0.38/aminer/pub.json , or ask @xiaotao.peng
recall_paper_text = '/data/zhuyifan/data/pub.json'

# path for loading and saving doc2vec model
d2v_model_path = '/data/cache/aminer/d2v.model'

# path for loading and saving lsa model
tfidf_model_path = '/data/cache/aminer/tfidf.model'
svd_model_path = '/data/cache/aminer/svd.model'

# path for finetuned SentenceBERT
sbert_model_path = '/data/cache/aminer/sbert-model-en-256seq'

```
For the first time running the code, the model will be trained so it may takes long, we have prepare some trained models, so that you can download it instead of training it.
* [Doc2vec](https://cloud.tsinghua.edu.cn/d/d2420f08f14b4de98eb6/)
* [LSA(TF-IDF)](https://cloud.tsinghua.edu.cn/d/85205abbde6d4dba9f08/)
* [OAG-BERT(Sim)](https://cloud.tsinghua.edu.cn/seafhttp/files/a951e516-652a-4307-b0b6-177ac08655e8/oagbert-v2-sim.zip)
* [Sentence-BERT(Finetuned)](https://cloud.tsinghua.edu.cn/f/656ea01e77e54c6ab1ea/?dl=1)

You can refer the `test_paper_emb.py` to see actual example to get embeedings of a paper.
Taking OAG-BERT as example, run the following script:
```bash
python test_paper_emb.py --model oag-bert
```
Currently, you may choose model name form {lsa, oag-bert, doc2vec}.

To generate a embedding of a paper, just import the specific model, and feed the texts:
```python
from paper_emb.tfidf import TFIDF_Emb

query = "machine learning"
model = TFIDF_Emb()
emb = model.get_emb(query)
```
However, when using oag-bert, the input should be a dict instead of a str, e,g.
```python
from paper_emb.oagbert import OAG_BERT_Emb

paper_example = {
    "title": "A paper title.", # Mandatory
    "abstract": "A paper abstract.", # Optional, used for both OAG and TF-IDF
    "keywords": ["word1", "word2", "word3"], # Optional, only required in OAG mode
    "venue": "a possible venue", # Optional, only required in OAG mode
    "authors": ["author 1", "author 2"], # Optional, only required in OAG mode
    "affiliations": ["org 1", "org 2", "org 3"] # Optional, only required in OAG mode
}

query_example =  {"title":"machine learning"}
model = OAG_BERT_Emb()
emb1 = model.get_emb(paper_example)
emb2 = model.get_emb(query_example)
```

### Notes

#### Calculate similarity between embeddings
Similarity between embeddings could be calculated by cosine similarity.

#### Finetune/Retrain the model
Remember, __Do retrain (i.e. call model.finetune())__ if the papers for embedding changed a lot, when you using the LSA or doc2vec model.
When finetuning the model, feed the model with a list of texts, e.g.
```python
finetune_texts = [
    "this is a sentence",
    "this is another sentence",
    "lalalalalala"
]

model.finetune(finetune_texts)
```


## Usage of Paper Recommndation

**STEP 1: **  Change the working directory to `/CF_recommendation/GFCF_rec/`.

**STEP 2:** Edit the file `world.py`, and:
* fill the `ROOT_PATH` which is the absolute path of `CF_recommendation` folder (e.g. `ROOT_PATH = "/home/zhuyifan/get-paper-embedding/CF_recommendation"`);
* fill the `PROD_PATH` which is the absolute path of data folder (e.g. `PROD_PATH = "/data/cache/aminer"`)

**STEP 3: ** When running the program, the model will load log data from `$PROD_PATH/input_log/YYYY-MM-DD-log.json`, where some example log files can be found at `/CF_recommendation/input_log/`. Similarly, the model will output log into  `$PROD_PATH/run_log/` and recommendation results into `$PROD_PATH/output_recommendation/`. The recommendation results wiil be zipped into json.gz file which is named as `cf_XXX_YYYY_MM_DD.json.gz` where XXX is the type of data ([report, topic, null for pub]), and an example is provided at `/CF_recommendation/output_recommendation/`.

**STEP 4: ** Run the shell for different task, three examples file are provided, which are `production_run_pub.sh`, `production_run_topic.sh`, `production_run_report.sh` for three different tasks.

**STEP 5: ** After making sure the whole procedure is workable, the add scripts into crobtab. An example is as follow (we have installed all required packages in conda base environment) :

```shell
crontab -e
#---------------------
SHELL=/bin/bash
PATH=/home/zhuyifan/anaconda3/bin:/home/zhuyifan/anaconda3/condabin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/zhuyifan/.local/bin:/home/zhuyifan/bin:/home/zhuyifan/.local/bin:/home/zhuyifan/bin
# m h  dom mon dow   command
0 5 * * * source activate base; /home/zhuyifan/get-paper-embedding/CF_recommendation/GFCF_rec/production_run_pub.sh; source deactivate
0 3 * * * source activate base; /home/zhuyifan/get-paper-embedding/CF_recommendation/GFCF_rec/production_run_report.sh; source deactivate
0 1 * * * source activate base; /home/zhuyifan/get-paper-embedding/CF_recommendation/GFCF_rec/production_run_topic.sh; source deactivate
```

## Acknowledgements
Special thanks to @Peng.Jiang, who fintuned the Sentence-BERT, and the results looks great!

This work is mainlly built by @yifan.zhu and @xiaotao.peng.