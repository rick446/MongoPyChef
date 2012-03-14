class Files(object):
    __name__ = 'files'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, checksum):
        return File(self, checksum)

    def __repr__(self):
        return '<Files>'

class File(object):

    def __init__(self, parent, checksum):
        self.__parent__ = parent
        self.__name__ = checksum
        self.request = parent.request
        self.filename = str(parent.request.account._id) + '/' + checksum

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<File %s>' % self.__name__

