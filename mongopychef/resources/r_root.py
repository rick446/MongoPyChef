from .r_client import Clients
from .r_cookbook import Cookbooks
from .r_databag import Databags
from .r_environment import Environments
from .r_node import Nodes
from .r_role import Roles
from .r_search import Search
from .r_sandbox import Sandboxes
from .r_file import Files

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

    def __getitem__(self, name):
        return self.children[name](self.request, self)
