from webob import exc
from .. import model as M
from .r_base import Resource

class Nodes(Resource):
    __name__ = 'nodes'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        return Node(self, name)

    def __repr__(self):
        return '<Nodes>'

class Node(Resource):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.node = parent.request.account.get_object(
            M.Node, name=name)
        if self.node is None:
            raise exc.HTTPNotFound()

    def __repr__(self):
        return '<Node %s>' % self.__name__

