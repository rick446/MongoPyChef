from webob import exc

class Resource(dict):
    __name__ = None
    __parent__ = None

    def allow_access(self, client, permission):
        return permission == 'read' or client.admin

class ResourceCollection(object):
    __name__ = None
    __model__ = None
    allow_new = False
    key_property='name'

    def __init__(self, request, parent, account):
        self.request = request
        self.__parent__ = parent
        self.account = account

    def allow_access(self, client, permission):
        return permission == 'read' or client.admin

    def __getitem__(self, name):
        obj = self.account.get_object(
            self.__model__, **{ self.key_property: name })
        if obj is None:
            if self.allow_new:
                obj = self.account.new_object(
                    self.__model__, **{ self.key_property: name })
            else:
                raise exc.HTTPNotFound()
        obj.__parent__ = self
        return obj

    def new_object(self, **kw):
        obj = self.account.new_object(
            self.__model__, **kw)
        obj.__parent__ = self
        return obj

    def decorate_child(self, obj):
        obj.__parent__ = self
        return obj

    def find(self, *args, **kwargs):
        kwargs.setdefault('decorate', self.decorate_child)
        return self.account.find_objects(
            self.__model__, *args, **kwargs)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
