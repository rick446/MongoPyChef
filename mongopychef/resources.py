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

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Client(self.request, self, name)

class Client(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        DENY_ALL ]

    def __init__(self, request, parent, name):
        self.request = request
        self.__parent__ = parent
        self.__name__ = name
        self.client = M.Client.query.get(
            account_id=request.client.account_id,
            name=name)
        if self.client is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if self.request.client.admin: return True
        if self.request.client._id == self.client._id: return True
        return False
        
    def __repr__(self):
        if self.client:
            return '<Client %s>' % self.client.name
        else:
            return '<Client None>'



