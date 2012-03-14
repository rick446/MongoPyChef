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
        self.name = name

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
        self.name = parent.name
        self.version = name

    def __repr__(self):
        return '<CookbookVersion %s => %s>' % (
            self.cookbook_name, self.__name__)

