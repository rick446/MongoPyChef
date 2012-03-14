import json

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config
from pyramid.exceptions import Forbidden

from ..resources import Clients, Client
from .. import model as M

