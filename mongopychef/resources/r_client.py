from webob import exc
from .. import model as M
from .r_base import Resource

class Clients(Resource):
    __name__ = 'clients'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        cli = self.request.account.get_object(
            M.Client, name=name)
        if cli is None:
            raise exc.HTTPNotFound()
        cli.__name__ = name
        cli.__parent__ = self
        return cli

    def __repr__(self):
        return '<Clients>'
