"""
Initializes elastic database with data from www.civicdata.com and www.sf-planning.org
Script must be run once on the host server using the command: python app_init.py
"""
from elasticsearch_dsl import connections
from sfip.importers.sfcivicdata import SFCivicDataImporter
from sfip.importers.sfplanning import SFPlanningNoticeImporter
from models import indices

connections.connections.create_connection(hosts=['localhost'], timeout=200)
map(lambda index: index.create(ignore=400), indices.values())

cdi = SFCivicDataImporter()
cdi.run(False)

pi = SFPlanningNoticeImporter('http://www.sf-planning.org/index.aspx?page=2735', False)
pi.run(False)