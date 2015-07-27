"""
Simple Flask app provides restless api access to database
"""
from flask import Flask
from elasticsearch_dsl import connections
from models import indices
from resources import *

api = Flask(__name__)

CaseResource.add_url_rules(api, rule_prefix='/api/cases/')
NoticeResource.add_url_rules(api, rule_prefix='/api/notices/')

if __name__ == '__main__':
    connections.connections.create_connection(hosts=['localhost'], timeout=200)

    map(lambda index: index.create(ignore=400), indices.values())

    api.debug = True
    api.run()
