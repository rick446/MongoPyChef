from webob import exc

class Resource(dict):
    __name__ = None
    __parent__ = None
    request=None

    def allow_access(self, client, permission):
        return permission == 'read' or client.admin

    def decorate_child(self, obj):
        obj.__parent__ = self
        obj.request = self.request
        return obj

class ResourceCollection(Resource):
    __name__ = None
    __model__ = None
    key_property='name'

    def __init__(self, request, parent, account):
        self.request = request
        self.__parent__ = parent
        self.account = account

    def __getitem__(self, name):
        obj = self.account.get_object(
            self.__model__, **{ self.key_property: name })
        if obj is None:
            raise exc.HTTPNotFound()
        return self.decorate_child(obj)

    def new_object(self, **kw):
        obj = self.account.new_object(
            self.__model__, **kw)
        return self.decorate_child(obj)

    def find(self, *args, **kwargs):
        kwargs.setdefault('decorate', self.decorate_child)
        return self.account.find_objects(
            self.__model__, *args, **kwargs)

    def __repr__(self): # pragma no cover
        return '<%s>' % self.__class__.__name__
