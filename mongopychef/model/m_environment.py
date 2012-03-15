import logging
from json import loads, dumps
from itertools import groupby

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session
from ..resources.r_base import Resource

log = logging.getLogger(__name__)

environment = collection(
    'chef.environment', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Field('default_attributes', str, if_missing='{}'),
    Field('override_attributes', str, if_missing='{}'),
    Field('description', str, if_missing=''),
    Field('cookbook_versions', { str: str }),
    Index('account_id', 'name', unique=True))

class EnvironmentCookbooks(Resource):
    __name__ = 'cookbooks'

    def __init__(self, parent):
        self.__parent__ = parent
        self.request = parent.request
        self.environment = parent.environment

    def __getitem__(self, name):
        return EnvironmentCookbook(self, name)

    def __repr__(self):
        return '<EnvironmentCookbooks %s>' % self.environment.name

class EnvironmentCookbook(Resource):

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request
        self.environment = parent.environment
        self.name = name

    def __repr__(self):
        return '<EnvironmentCookbook %s => %s>' % (
            self.environment.name, self.__name__)

class EnvironmentCookbookVersions(Resource):
    __name__ = 'cookbook_versions'

    def __init__(self, parent):
        self.__parent__ = parent
        self.parent = parent
        self.request = parent.request
        self.environment = parent.environment

    def __repr__(self):
        return '<EnvironmentCookbookVersions %s>' % self.parent.name

class Environment(ModelBase):
    children = dict(
        cookbooks=EnvironmentCookbooks,
        data=EnvironmentCookbookVersions)

    @property
    def __name__(self):
        return self.name

    def __getitem__(self, name):
        return self.children[name](self)

    def __json__(self):
        return dict(
            chef_type='environment',
            json_class='Chef::Environment',
            name=self.name,
            description=self.description,
            default_attributes=loads(self.default_attributes),
            override_attributes=loads(self.override_attributes),
            cookbook_versions=self.cookbook_versions)

    def update(self, d):
        self.name = d['name']
        self.description = d['description']
        self.default_attributes = dumps(d['default_attributes'])
        self.override_attributes = dumps(d['override_attributes'])
        self.cookbook_versions = d['cookbook_versions']

    def filter_cookbooks(self, name, iter):
        version = self.cookbook_versions.get(name, None)
        if version is None:
            return iter
        else:
            return ( cb for cb in iter if cb.version == version)

    def get_cookbook_versions(self, run_list=None):
        from .m_cookbook import CookbookVersion
        from ..lib.runlist import expand_runlist
        if run_list is None:
            q = CookbookVersion.query.find(dict(
                    account_id=self.account_id))
        else:
            cookbook_names = list(expand_runlist(
                    self.account._id, run_list, self))
            q = CookbookVersion.query.find(dict(
                    account_id=self.account_id,
                    name={'$in':cookbook_names}))
        result = {}
        for name, cookbooks in groupby(q, key=lambda cb:cb.name):
            cookbooks = sorted(cookbooks, key=lambda cb:cb.version_vector)
            cookbooks = list(self.filter_cookbooks(name, cookbooks))
            result[name] = cookbooks[0]
        return result

orm_session.mapper(Environment, environment, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))
