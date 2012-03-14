from webob import exc
from .. import model as M

class Sandboxs(object):
    __name__ = 'sandboxs'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Sandbox(self, name)

    def __repr__(self):
        return '<Sandboxs>'

class Sandbox(object):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.sandbox = parent.request.account.get_object(
            M.Sandbox, _id=name)
        if self.sandbox is None:
            raise exc.HTTPNotFound()

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __getitem__(self, checksum):
        return SandboxFile(self, checksum)

    def __repr__(self):
        return '<Sandbox %s>' % self.sandbox._id

class SandboxFile(object):

    def __init__(self, parent, checksum):
        self.__parent__ = parent
        self.__name__ = checksum
        self.request = parent.request
        self.file = parent.sandbox.get_file(checksum)
        if self.item is None:
            raise exc.HTTPNotFound()
            
    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False
        
    def __repr__(self):
        return '<SandboxFile %s => %s>' % (
            self.sandbox._id, self.checksum)
