"""
Updates elastic database with new data from www.civicdata.com and www.sf-planning.org
Script should be run on server as a cron job at least once a week.
SF planning website updates its notice of hearings data every friday.
"""
from elasticsearch_dsl import connections
from importers.sfcivicdata import SFCivicDataImporter
from importers.sfplanning import SFPlanningNoticeImporter

connections.connections.create_connection(hosts=['localhost'], timeout=200)

cdi = SFCivicDataImporter()
cdi.run(True)

pi = SFPlanningNoticeImporter('http://www.sf-planning.org/index.aspx?page=2735', False)
pi.run(True)
