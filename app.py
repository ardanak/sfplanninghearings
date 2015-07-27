"""
Updates elastic database with new data from www.civicdata.com and www.sf-planning.org
Script should be run on server as a cron job at least once a week.
SF planning website updates its notice of hearings data every friday.
"""
from elasticsearch_dsl import connections
from sfip.importers.sfcivicdata import SFCivicDataImporter
from sfip.importers.sfplanning import SFPlanningNoticeImporter
from models import indices

connections.connections.create_connection(hosts=['localhost'], timeout=200)
map(lambda index: index.create(ignore=400), indices.values())

cdi = SFCivicDataImporter()
cdi.run(True)

pi = SFPlanningNoticeImporter('http://www.sf-planning.org/index.aspx?page=2735', False)
pi.run(True)