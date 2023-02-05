# OAG_BERT Emdedding

Train a vector representation from the file pub.json by oag_bert.

- input file:
pub.json
- output file:
pour the vector into the milvus

## Requirements and Installation

Requirements:

- Python version >= 3.6

We also use the following packages, which you may install via `pip install -r requirements.txt`

- nmslib==2.1.1
- sentence-transformers=2.2.0
- spacy==3.4.1
- en_core_web_sm-3.4.0.tar.gz

## Usage

First, modify the storage path for the "oag_bert model" and the storage path for the input file "pub.json" in "config.py". If the output file "cache" folder does not exist in the path you just modified, this program will automatically create it. We also offer you the following ways to operate this program:

- The data we process is incremental and needs to be run the first time it is used
 you can enter the following command:

  ```sh
  $ python3 embedding/run.py
  ```
- Others 
- '--model', type=str, default='oag-bert', help='Select a model from \{oag-bert, sentence-bert, tfidf\}'
- "--limit", default=-1, type=int
- "--cores", default=multiprocessing.cpu_count()//4, type=int
- "--cache", action="store_false"  ==>  Use of save result
- "--load_cache", action="store_false" ==>    Use of load embed data

To use this program, just clone this repo and copy the `embedding` folder to your project.
