import logging
from json import loads, dumps

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

role = collection(
    'chef.role', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Field('description', str),
    Field('default_attributes', str),
    Field('override_attributes', str),
    Field('run_list', [ str ] ),
    Field('env_run_lists', { str: [ str ]}),
    Index('account_id', 'name', unique=True))

class Role(object):

    def url(self):
        return request.relative_url(
            config.chef_api_root + '/roles/' + self.name)

    def __json__(self):
        return dict(
            chef_type='role',
            json_class='Chef::Role',
            name=self.name,
            description=self.description,
            default_attributes=loads(self.default_attributes),
            override_attributes=loads(self.override_attributes),
            env_run_lists=self.env_run_lists,
            run_list=self.run_list)

    def update(self, d):
        self.name = d['name']
        self.description = d['description']
        self.default_attributes = dumps(d['default_attributes'])
        self.override_attributes = dumps(d['override_attributes'])
        self.env_run_lists=d['env_run_lists']
        self.run_list = d['run_list']

orm_session.mapper(Role, role, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))


