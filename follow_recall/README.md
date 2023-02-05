# Recall papers based on followed scholars by users  

To recall papers based on followed scholars by using the pool of highly cited papers and the dynamic pool of scholars. We recall papers of three kind of scholars:  

* Scholars who are followed by user    
* Scholars who are similar to followed scholars who are followed by user   
* Scholars who are collaborators or teachers or students of followed scholars.

## 	Requirements and installation

Requirements:  

* Python version >= 3.6

We also use the following packages, which you may install via `pip install -r requirements.txt`.  

* requests   
* pymongo
* pyssdb
* bson
* psycopg2-binary


## Usage

First, please modify the file path of corpus in `config.py`. And what you can set by yourself are follows:  

* Set the start time for calculating distance by `start_time`
* Set the period of active users by `active_start_time` and `active_end_time`   
* Set the number of similar authors by `sim_authors_num`  
* Set the number of highly cited papers and latest papers you want to recall by `recall_number_of_high` and `recall_number_of_new`   
* Set the level of logs by `LOG_LEVEL`

And then run `run.py` to obtain the list of papers that include highly cited papers and latest papers of three kind of scholars mentioned above.

To use this toolbox, just clone this repo and copy the `paper_recall` folder to your project.

## Notes

* The struct of every roll in generated json file is like this:
```python
{"uid":[{"id_of_followed":"",
         "name_of_followed_author":"",
         "name_of_followed_author":"",
         "chinese_name_of_followed_author":"",
         "papers":{"highly_cited_papers":[{"paper_id":"","distance":"","label":"","new":"","n_citation":"","author_id":"","author_name_en":"","author_name_zh":"","pv":"","zone":""}],
                   "latest_papers":[{"paper_id":"","distance":"","label":"","new":"","n_citation":"","author_id":"","author_name_en":"","author_name_zh":"","pv":"","zone":""}]
         }
        ,....]
 }
```
* The value of label in generated file is "followed_scholar"  or  "cooperation_scholar" or "similar_scholar" to label the three kind of scholars' papers.