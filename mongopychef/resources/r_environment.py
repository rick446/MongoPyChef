from webob import exc
from .. import model as M

class Environments(object):
    __name__ = 'environments'

    def __init__(self, request, parent):
        self.request = request
        self.__parent__ = parent

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return Environment(self, name)

    def __repr__(self):
        return '<Environments>'

class Environment(dict):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.environment = parent.request.account.get_item(
            M.Environment, name=name)
        self['cookbooks'] = EnvironmentCookbooks(self)
        self['cookbook_versions'] = EnvironmentCookbookVersions(self)

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<Environment %s>' % self.__name__

class EnvironmentCookbooks(object):
    __name__ = 'cookbooks'

    def __init__(self, parent):
        self.__parent__ = parent
        self.request = parent.request
        self.environment = parent.envrionment

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __getitem__(self, name):
        return EnvironmentCookbook(self, name)

    def __repr__(self):
        return '<EnvironmentCookbooks %s>' % self.environment.name

class EnvironmentCookbook(dict):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.environment = parent.environment
        self.name = name

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<EnvironmentCookbook %s => %s>' % (
            self.environment.name, self.__name__)

class EnvironmentCookbookVersions(object):
    __name__ = 'cookbook_versions'

    def __init__(self, parent):
        self.__parent__ = parent
        self.request = parent.request
        self.environment = parent.envrionment

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<EnvironmentCookbookVersions %s>' % self.environment.name

class EnvironmentCookbook(dict):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.environment = parent.environment
        self.name = name

    def allow_access(self, permission):
        if permission == 'view': return True
        if self.request.client.admin: return True
        return False

    def __repr__(self):
        return '<EnvironmentCookbook %s => %s>' % (
            self.environment.name, self.__name__)

