from datetime import datetime, date
import dateutil.parser
from sfip.models import Importer
from sfip.resources import *

class DataImporter(object):
    """ DataImporter base class """
    importer_name = 'generic'
    
    def __init__(self):
        pass

    def fetch(self, last_updated=datetime(1900, 1, 1)):
        return []

    def run(self, initialized):
        importer_model = Importer.get(id=self.importer_name, ignore=404)
        if importer_model is None:
            importer_model = Importer(_id=self.importer_name, last_updated=datetime(1900, 1, 1))
            importer_model.save()

        try:
            for doc_type, doc in self.fetch(importer_model.last_updated):
                if doc_type == 'case':
                    model = Case.get(id=doc['case_id'], ignore=404)
                    if model is None:
                        model = Case(_id=doc['case_id'], **doc)
                        model.save()
                    elif model.last_updated < dateutil.parser.parse(doc['last_updated']):
                        model.update(**doc)
                elif doc_type == 'notice':
                    if doc['date_published'] > doc['last_updated'] or (initialized == False):
                        case_id = str(doc['case_num'].strip()+doc['case_code'].strip())
                        existing_case = Case.get(id=case_id, ignore=404)
                        if existing_case is None:
                            case_doc = {
                                'case_id': case_id,
                                'last_updated': doc['last_updated'],
                                'address': doc['address'],
                                'name': 'NEWCASE'
                            }
                            new_case = Case(_id=case_id, **case_doc)
                            new_case.save()
                            model = Notice(**doc)
                            model.meta.parent = case_id
                            model.save()
                        else:
                            model = Notice(**doc)
                            model.meta.parent = case_id
                            model.save()
                else:
                    continue

                importer_model.last_updated = doc['last_updated']
        finally:
            importer_model.save()