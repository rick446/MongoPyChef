from webob import exc
from pyramid.security import Everyone, Allow, DENY_ALL

from mongopychef import model as M

class Root(dict):
    __name__ = ''

    def __init__(self, request):
        self.request = request
        self['clients'] = Clients(request, self)

class Clients(object):
    __name__ = 'clients'
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:admins', 'add'),
        DENY_ALL ]

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        return Client(self.request, self, name)

class Client(object):

    def __init__(self, request, parent, name):
        self.request = request
        self.__parent__ = parent
        self.__name__ = name
        self.client = M.Client.query.get(name=name)
        if self.client is None:
            raise exc.HTTPNotFound()

    def __repr__(self):
        if self.client:
            return '<Client %s>' % self.client.name
        else:
            return '<Client None>'


