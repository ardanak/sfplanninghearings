from restless.fl import FlaskResource
from urlparse import urlparse
from urlparse import parse_qs

from models import Case, Notice

class ESResource(FlaskResource):
    model_class = None

    def __init__(self, *args, **kwargs):
        if self.model_class is None:
            raise ValueError("must override model_class")

        super(ESResource, self).__init__(*args, **kwargs)

    def is_authenticated(self):
        return True

    def list(self):
        s = self.model_class.search()
        params = parse_qs(urlparse(self.request.url)[4])

        limit = int(params.get('limit', [20])[0])

        if 'q' in params:
            s = s.query('query_string', query=params['q'][0])

        s = s.extra(size=limit)

        return map(lambda m: m.to_dict(), s.execute())

    def detail(self, pk):
        return self.model_class.get(id=pk).to_dict()

    def create(self):
        model = self.model_class(**self.data)
        model.save()
        return model.to_dict()

    def update(self, pk):
        model = self.model_class.get(id=pk, ignore=404)
        if model is None:
            model = self.model_class(_id=pk, **self.data)
            model.save()
        else:
            model.update(**self.data)
        return model.to_dict()

    def delete(self, pk):
        self.model_class.get(id=pk).delete()

class CaseResource(ESResource):
    model_class = Case

class NoticeResource(ESResource):
    model_class = Notice