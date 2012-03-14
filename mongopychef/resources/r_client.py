from webob import exc
from .. import model as M
from .r_base import Resource

class Clients(Resource):
    __name__ = 'clients'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        return Client(self, name)

    def __repr__(self):
        return '<Clients>'

class Client(Resource):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.client = parent.request.account.get_object(
            M.Client, name=name)
        if self.client is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'delete':
            return (self.request.client.admin
                    and self.request.client is not self.client)
        return super(Client, self).allow_access(permission)
        
    def __repr__(self):
        if self.client:
            return '<Client %s>' % self.client.name
        else:
            return '<Client None>'

