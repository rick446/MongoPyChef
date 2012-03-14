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

#     def __getitem__(self, name):
#         return CookbookVersion(self.request, self, name)

#     def __repr__(self):
#         return '<Cookbook %s>' % self.__name__

# class CookbookVersion(Resource):

#     def __init__(self, parent, name):
#         self.__parent__ = parent
#         self.__name__ = name
#         self.request = parent.request
#         self.name = parent.name
#         self.version = name

#     def __repr__(self):
#         return '<CookbookVersion %s => %s>' % (
#             self.cookbook_name, self.__name__)

