import requests
from elasticsearch_dsl import connections
from datetime import datetime
from base import DataImporter

class SFCivicDataImporter(DataImporter):
    """ Fetch records from www.civicdata.com """

    importer_name = 'sfcivicdata'

    def __init__(self, resource_id='32fee353-3469-4307-bdcd-54ddbe9b5fae'):
        self._resource_id = resource_id

    def fetch(self, last_updated=datetime(1900, 1, 1)):
        ckan_url = "http://www.civicdata.com/api/action/datastore_search_sql"
        batch_size = 1000

        ckan_count_query = """
            SELECT count(1) FROM "%s" WHERE "LAST UPDATED" >= '%s'
        """ % (self._resource_id, last_updated.strftime("%Y-%m-%dT%H:%M:%S.000"))

        count_response = requests.get(ckan_url, params={"sql": ckan_count_query.strip()})
        record_count = int(count_response.json()["result"]["records"][0]["count"])

        i = 0
        while i < record_count:
            ckan_sql = """
                SELECT *
                  FROM "%s"
                 WHERE "LAST UPDATED" >= '%s'
                 ORDER BY "LAST UPDATED"
                 LIMIT %d
                OFFSET %d
            """ % (
                self._resource_id,
                last_updated.strftime("%Y-%m-%dT%H:%M:%S.000"),
                batch_size,
                i
            )

            i += batch_size

            res = requests.get(ckan_url, params={"sql": ckan_sql.strip()})

            for raw_record in res.json()["result"]["records"]:
                record_id = raw_record['RECORD ID'].replace('-', '').replace('.', '')
                record = {
                    'case_id': record_id,
                    'name': raw_record['RECORD NAME'],
                    #raw_record['RECORD TYPE'],
                    #raw_record['DATE OPENED'],
                    #raw_record['RECORD STATUS'],
                    #raw_record['RECORD STATUS DATE'],
                    'address': raw_record['ADDRESS'],
                    #raw_record['DATE CLOSED'],
                    #raw_record['DESCRIPTION'],
                    #raw_record['SHORT NOTES'],
                    #raw_record['PLANNER NAME'],
                    #raw_record['PLANNER PHONE'],
                    #raw_record['PLANNER EMAIL'],
                    'last_updated': raw_record['LAST UPDATED'],
                }
                yield ('case', record)