import logging

from webob import exc

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

databag = collection(
    'chef.databag', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Index('account_id', 'name', unique=True))

databag_item = collection(
    'chef.databag_item', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('databag_id',S.ObjectId(if_missing=None)),
    Field('id', str),
    Field('data', str),
    Index('account_id', 'databag_id', 'id', unique=True))

class Databag(ModelBase): 

    def __getitem__(self, name):
        obj = self.account.get_object(
            DatabagItem, databag_id=self._id, id=name)
        if obj is None:
            raise exc.HTTPNotFound()
        obj.__name__ = name
        obj.__parent__ = self
        return obj

class DatabagItem(ModelBase):  pass

orm_session.mapper(Databag, databag, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account'),
        items=RelationProperty('DatabagItem')))

orm_session.mapper(DatabagItem, databag_item, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account'),
        databag_id=ForeignIdProperty('Databag'),
        databag=RelationProperty('Databag')))

