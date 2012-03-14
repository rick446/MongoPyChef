import logging
from json import loads, dumps
from itertools import groupby

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

environment = collection(
    'chef.environment', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Field('default_attributes', str),
    Field('override_attributes', str),
    Field('description', str),
    Field('cookbook_versions', { str: str }),
    Index('account_id', 'name', unique=True))

class Environment(ModelBase): 

    def url(self):
        return request.relative_url(
            config.chef_api_root + '/environment/' + self.name)

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
