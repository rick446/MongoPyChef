import os
import logging

import bson
from Crypto.PublicKey import RSA

from ming import collection, Field
from ming import schema as S
from ming.odm import RelationProperty, ForeignIdProperty, Mapper
from ming.utils import LazyProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

client = collection(
    'chef.client', doc_session,
    Field('_id', S.ObjectId()),
    Field('name', str, unique=True),
    Field('account_id', S.ObjectId()),
    Field('raw_public_key', S.Binary()),
    Field('is_validator', bool, if_missing=False),
    Field('admin', bool, if_missing=False))

class Client(ModelBase):

    @property
    def __name__(self):
        return self.name

    def allow_access(self, client, permission):
        if permission == 'delete':
            return (
                client.admin
                and client is not self
                and not self.is_validator)
        return super(Client, self).allow_access(client, permission)

    def regenerate_key(self, strength=2048):
        private = RSA.generate(strength, os.urandom)
        self.raw_public_key=bson.Binary(private.publickey().exportKey())
        return private
        
    @classmethod
    def generate(cls, account,
                 name=None, admin=False,
                 private_key=None, strength=2048):
        if private_key is None:
            private = RSA.generate(strength)
        else:
            private = private_key
        kwargs = dict(
            account_id=account._id,
            admin=admin,
            raw_public_key=bson.Binary(private.publickey().exportKey()))
        if name is None:
            kwargs['name'] = account.shortname + '-validator'
            kwargs['is_validator'] = True
            kwargs['admin'] = True
        else:
            kwargs['name'] = name
        result = cls(**kwargs)
        return result, private

    def __json__(self):
        return dict(
            chef_type='client',
            json_class='Chef::ApiClient',
            name=self.name,
            public_key=self.raw_public_key,
            rev=None,
            admin=self.admin)

    def update(self, d):
        result = self.__json__()
        self.admin = d['admin']
        if d.get('private_key'):
            key = self.regenerate_key()
            result['private_key'] = key.exportKey()
        return result

    @LazyProperty
    def key(self):
        return RSA.importKey(self.raw_public_key)

orm_session.mapper(Client, client, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))

Mapper.compile_all()
