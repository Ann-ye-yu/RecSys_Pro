import flask
import json
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from run import run
from run import load_file_from_disk
from common.pymilvus_connection import PymilvusConnection
from flask import request

server = flask.Flask(__name__)

pub_json = load_file_from_disk()
milvus = PymilvusConnection()
conn = milvus.get_embedding_collection()
logging.basicConfig(filename='similar_paper_recall_logger.log', level=logging.INFO)


@server.route('/similar_paper_recall', methods=['post'])
def similar_paper_recall():
    obj = request.get_json()
    try:
        pid_list = obj['pid_list']
        logging.info(f'Similar_papers_recall module request pid_list is {pid_list}')
        data = dict()
        wrong_pid_list = list()
        for pid in pid_list:
            logging.info(f'get similar paper from milvus and MeiliSearch, target pid={pid}')
            if pid in pub_json:
                data[pid] = run(pid, pub_json, conn)
            else:
                logging.info(f'pid={pid} not in pub.json.')
                wrong_pid_list.append(pid)
        return json.dumps({
            'success': True,
            'msg': 'success',
            'data': data,
            'wrong_pid_list': wrong_pid_list,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'msg': str(e),
        })


if __name__ == '__main__':
    server.run(debug=False, port=12345, host='0.0.0.0')
