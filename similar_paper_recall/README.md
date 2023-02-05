### Similar Papers Recall
Here, we recall similar papers from both paths:

- recall top5 from milvus via pid.
- recall top5 from MeiliSearch via keywords of target papers. besides, if there are no keywords in the paper, we will first generate them algorithmically.

### Requirements and installation

Requirements:

- Python version >= 3.9

We also use the following packages, which you may install via `pip install -r requirements.txt`

- requests
- pymilvus 
- flask

### Usage of Get Similar Papers of a Paper

we provide an API service to recall similar papers.  Therefore, you just need to deploy our service to the server and call it through the POST request.

##### Deploy

- use `python api_server.py` to run our program.

##### Usage

Send a `POST` request to `http://10.10.0.29:12345/similar_paper_recall`

request body:

```python
# request params:
{
    "pid_list": [pid, ...]  # where pid is the same as id_of_mysql in pub.json.
}

# for example:
{
    "pid_list" : [526810, 526809, 526805],
}

# and the returns: 
{
    "success": true, 
    "msg": "success",
    "data": {
        "pid": [
            {
                "_id": pub_id, # e.g., 627a43cd5aee126c0f2a28ef
                "tags": list,  # e.g., ["SCI", "CCFA", "Arxiv"],
                "title": str,
                ...
            },
            ...
        ],
        ...
    },
    # If the pid does not appear in the pub.json file, it will appear here.
    "wrong_pid_list": list  # e.g., [526809, 526805]
}

# Or.
{
    "success"： false,
    "msg": str, # error_code
}
```

##### Attention:

**The default is to recall Top5 from Milvus, but the `pid` returned from Milvus may not be in the currently loaded `pub.json` file, so the actual number of recalls is <=5.**

