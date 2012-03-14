from .r_base import Resource

class Files(Resource):
    __name__ = 'files'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, checksum):
        return File(self, checksum)

    def __repr__(self):
        return '<Files>'

class File(Resource):

    def __init__(self, parent, checksum):
        self.__parent__ = parent
        self.__name__ = checksum
        self.request = parent.request
        self.filename = str(parent.request.account._id) + '/' + checksum

    def __repr__(self):
        return '<File %s>' % self.__name__

