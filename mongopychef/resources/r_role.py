from webob import exc
from .. import model as M
from .r_base import Resource

class Roles(Resource):
    __name__ = 'roles'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        obj = self.request.account.get_object(
            M.Role, name=name)
        if obj is None:
            raise exc.HTTPNotFound()
        obj.__name__ = name
        obj.__parent__ = self
        return obj

    def __repr__(self):
        return '<Roles>'

