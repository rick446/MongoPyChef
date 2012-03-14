from webob import exc
from .. import model as M

class Roles(object):
    __name__ = 'roles'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Role(self, name)

    def __repr__(self):
        return '<Roles>'

class Role(object):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.role = parent.request.account.get_item(
            M.Role, name=name)
        if self.role is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<Role %s>' % self.__name__

