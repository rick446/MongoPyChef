from webob import exc
from .. import model as M

class Databags(object):
    __name__ = 'databags'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Databag(self, name)

    def __repr__(self):
        return '<Databags>'

class Databag(object):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.databag = parent.request.account.get_object(
            M.Databag, name=name)
        if self.databag is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __getitem__(self, name):
        return Databag(self.request, self, name)

    def __repr__(self):
        return '<Databag %s>' % self.databag.name

class DatabagItem(object):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.item = parent.databag.get_item(name)
        if self.item is None:
            raise exc.HTTPNotFound()
            
    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __repr__(self):
        return '<DatabagItem %s => %s>' % (
            self.__parent__.__name__, self.__name__)

