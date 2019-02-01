from jobs.yamlParser import YamlParser
from elasticsearch import Elasticsearch
import requests


#   Connection verification to elastic server
def connection_test():
    try:
        r = requests.get('http://localhost:9200')
        if r.status_code != 200:
            print("Server elasticsearch error : {}".format(r.status_code))
            return None
        return Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    except:
        print("Can't connect to elasticsearch server.")
        return None


# Insert a dict to elk
def index_json(dict_json, match_id):
    yp = YamlParser()
    es = connection_test()
    if not es:
        return False

    result = es.index(index=yp.index_name, doc_type=yp.type_name, body=dict_json, id=match_id)
    return result


# Search throw the elastic server
def check_list_match(id_game):
    yp = YamlParser()
    es = connection_test()
    if not es:
        return False
    return es.mget(index=yp.index_name, doc_type=yp.type_name, body={"ids": [str(i) for i in id_game]})


