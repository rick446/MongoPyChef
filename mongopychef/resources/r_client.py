from webob import exc
from .. import model as M

class Clients(object):
    __name__ = 'clients'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Client(self, name)

    def __repr__(self):
        return '<Clients>'

class Client(object):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.client = parent.request.account.get_object(
            M.Client, name=name)
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

