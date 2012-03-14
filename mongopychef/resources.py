from webob import exc
from pyramid.security import Everyone, Allow, DENY_ALL

from mongopychef import model as M

class Root(dict):
    __name__ = ''

    def __init__(self, request):
        self.request = request
        self['clients'] = Clients(request, self)
        self['nodes'] = Nodes(request, self)
        self['cookbooks'] = Cookbooks(request, self)

class Cookbooks(object):
    __name__ = 'cookbooks'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent
        
    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Cookbook(self.request, self, name)

    def __repr__(self):
        return '<Cookbooks>'

class Cookbook(object):

    def __init__(self, request, parent, name):
        self.request = request
        self.__parent__ = parent
        self.__name__ = name
        self.cookbook_name = name

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getattr__(self, name):
        return CookbookVersion(self.request, self, name)

    def __repr__(self):
        return '<Cookbook %s>' % self.__name__

class CookbookVersion(object):

    def __init__(self, request, parent, name):
        self.request = request
        self.__parent__ = parent
        self.__name__ = name
        self.cookbook_version = name

    def __repr__(self):
        return '<CookbookVersion %s => %s>' % (
            self.cookbook_name, self.__name__)

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
        return Client(self.request, self, name)

    def __repr__(self):
        return '<Clients>'

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
        return Node(self.request, self, name)

    def __repr__(self):
        return '<Nodes>'

class Client(object):

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

class Node(dict):

    def __init__(self, request, parent, name):
        self.request = request
        self.__parent__ = parent
        self.__name__ = name
        self.node = M.Node.query.get(
            account_id=request.client.account_id,
            name=name)
        if self.node is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __repr__(self):
        return '<Node %s>' % self.__name__

