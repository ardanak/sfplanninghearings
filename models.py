from elasticsearch_dsl import Index, DocType, String, Date, Object, MetaField

indices = { x: Index(x) for x in ['cases', 'notices', 'importers'] }

indices['importers'].settings(
    number_of_shards=1
)

class Case(DocType):
    case_id = String()
    last_updated = Date(format="date_optional_time")
    address = String()
    name = String()

class Notice(DocType):
    date_published = String()
    hearing_date = String()
    last_updated = Date(format="date_optional_time")
    case_num = String()
    case_code = String()
    address = String()
    announcement = String()
    links = Object(
        multi=True,
        properties={
            'name' : String(),
            'href' : String()
        }
    )
    images = Object(
        multi=True,
        properties={
            'source' : String(),
            'description' : String()
        }
    )

    class Meta:
        parent = MetaField(type='case')

class Importer(DocType):
    last_updated = Date(format="date_optional_time")

indices['cases'].doc_type(Case)
indices['notices'].doc_type(Notice)
indices['importers'].doc_type(Importer)
