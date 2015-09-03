"""
Simple Flask app provides restless api access to database
"""
from flask import Flask
from elasticsearch_dsl import connections
from resources import *

api = Flask(__name__)

CaseResource.add_url_rules(api, rule_prefix='/api/cases/')
NoticeResource.add_url_rules(api, rule_prefix='/api/notices/')

if __name__ == '__main__':
    connections.connections.create_connection(hosts=['localhost'], timeout=200)

    api.debug = False
    # Add host='x.x.x.x' inside run() to use your production server's ip address
    api.run()
