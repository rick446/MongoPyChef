from .r_base import ResourceCollection

from .. import model as M

from .r_cookbook import Cookbooks
from .r_databag import Databags
from .r_environment import Environments
from .r_search import Search
from .r_sandbox import Sandboxes

class Clients(ResourceCollection):
    __name__ = 'clients'
    __model__ = M.Client

class Nodes(ResourceCollection):
    __name__ = 'nodes'
    __model__ = M.Node

class Roles(ResourceCollection):
    __name__ = 'roles'
    __model__ = M.Role

class Files(ResourceCollection):
    __name__ = 'files'
    __model__ = M.ChefFile
    allow_new = True

class Root(dict):
    __name__ = ''
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

