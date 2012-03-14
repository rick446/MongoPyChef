from webob import exc
from .. import model as M

class Nodes(object):
    __name__ = 'nodes'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Node(self, name)

    def __repr__(self):
        return '<Nodes>'

class Node(dict):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.node = parent.request.account.get_item(
            M.Node, name=name)
        if self.node is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __repr__(self):
        return '<Node %s>' % self.__name__

