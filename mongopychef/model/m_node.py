import logging
from json import loads, dumps

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

node = collection(
    'chef.node', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Field('chef_environment', str, if_missing='_default'),
    Field('normal', str, if_missing='{}'),
    Field('default', str, if_missing='{}'),
    Field('override', str, if_missing='{}'),
    Field('automatic', str, if_missing='{}'),
    Field('run_list', [ str ] ),
    Index('account_id', 'name', unique=True))

class Node(ModelBase):

    @property
    def __name__(self):
        return self.name

    def __json__(self):
        return dict(
            chef_type='node',
            json_class='Chef::Node',
            name=self.name,
            chef_environment=self.chef_environment,
            normal=loads(self.normal),
            default=loads(self.default),
            override=loads(self.override),
            automatic=loads(self.automatic),
            run_list=self.run_list)

    def update(self, d):
        if 'name' in d:
            self.name = d['name']
        self.chef_environment = d['chef_environment']
        self.normal=dumps(d['normal'])
        self.default=dumps(d['default'])
        self.override=dumps(d['override'])
        self.automatic=dumps(d['automatic'])
        self.run_list = d['run_list']


orm_session.mapper(Node, node, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))


