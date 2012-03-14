from .r_base import ResourceCollection

from .. import model as M

from .r_cookbook import Cookbooks
from .r_environment import Environments
from .r_search import Search

class Clients(ResourceCollection):
    __name__ = 'clients'
    __model__ = M.Client

class Databags(ResourceCollection):
    __name__ = 'data'
    __model__ = M.Databag

class Nodes(ResourceCollection):
    __name__ = 'nodes'
    __model__ = M.Node

class Roles(ResourceCollection):
    __name__ = 'roles'
    __model__ = M.Role

class Files(ResourceCollection):
    __name__ = 'files'
    __model__ = M.ChefFile
    key_property = '_id'

class Sandboxes(ResourceCollection):
    __name__ = 'sandboxes'
    __model__ = M.Sandbox
    key_property = '_id'

class Root(dict):
    __name__ = ''
    __parent__ = None
    children = dict(
        clients=Clients,
        cookbooks=Cookbooks,
        data=Databags,
        environments=Environments,
        nodes=Nodes,
        roles=Roles,
        search=Search,
        sandboxes=Sandboxes,
        files=Files)

    def __init__(self, request):
        self.request = request
        self.account = request.account

    def __getitem__(self, name):
        return self.children[name](self.request, self, self.account)

