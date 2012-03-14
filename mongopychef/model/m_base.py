from ming import schema as S

class ModelBase(object):

    def allow_access(self, client, permission):
        return permission == 'read' or client.admin

    def decorate_child(self, obj):
        obj.__parent__ = self
        return obj

class CookbookFile(S.Object):

    def __init__(self):
        super(CookbookFile, self).__init__(
            fields=dict(
                name=S.String(),
                url=S.String(),
                checksum=S.String(),
                path=S.String(),
                specificity=S.String()))

    @classmethod
    def url_for(cls, request, checksum):
        return request.relative_url(
            '/files/' + checksum)

    def _validate(self, d, **kwargs):
        r = super(CookbookFile, self)._validate(d, **kwargs)
        if r['url'] is None:
            r['url'] = self.url_for(r['checksum'])
        return r

    
