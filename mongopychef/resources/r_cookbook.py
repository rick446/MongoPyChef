from .. import model as M

from .r_base import Resource, ResourceCollection

class Cookbooks(Resource):
    __name__ = 'cookbooks'

    def __init__(self, request, parent, account):
        self.__parent__ = parent
        self.request = request
        self.account = account
        
    def __getitem__(self, name):
        return Cookbook(self, name)

    def __repr__(self):
        return '<Cookbooks>'

class Cookbook(ResourceCollection):
    __model__ = M.CookbookVersion

    def __init__(self, parent, name):
        self.__name__ = name
        self.name = name
        super(Cookbook, self).__init__(parent.request, parent, parent.account)

