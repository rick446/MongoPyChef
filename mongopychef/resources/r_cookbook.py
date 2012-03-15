from webob import exc

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

    def __repr__(self):
        return '<Cookbook %s>' % self.name

    def find(self, *args, **kwargs):
        if len(args) == 0: args = ({},)
        args[0]['cookbook_name'] = self.name
        return super(Cookbook, self).find(*args, **kwargs)

    def __getitem__(self, version):
        obj = self.find(dict(version=version)).first()
        if obj is None:
            raise exc.HTTPNotFound()
        obj.__parent__ = self
        return obj

    

