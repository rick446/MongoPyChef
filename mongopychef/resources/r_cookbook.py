from .r_base import Resource

class Cookbooks(Resource):
    __name__ = 'cookbooks'

    def __init__(self, request, parent):
        self.__parent__ = parent
        self.request = request
        
    def __getitem__(self, name):
        return Cookbook(self, name)

    def __repr__(self):
        return '<Cookbooks>'

class Cookbook(Resource):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.name = name

    def __getitem__(self, name):
        return CookbookVersion(self.request, self, name)

    def __repr__(self):
        return '<Cookbook %s>' % self.__name__

class CookbookVersion(Resource):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.name = parent.name
        self.version = name

    def __repr__(self):
        return '<CookbookVersion %s => %s>' % (
            self.cookbook_name, self.__name__)

