import logging

import bson
from Crypto.PublicKey import RSA

from ming import collection, Field
from ming import schema as S
from ming.odm import RelationProperty, ForeignIdProperty, Mapper
from ming.utils import LazyProperty

from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

client = collection(
    'chef.client', doc_session,
    Field('_id', S.ObjectId()),
    Field('name', str, unique=True),
    Field('account_id', S.ObjectId()),
    Field('user_id', S.ObjectId, if_missing=None),
    Field('raw_public_key', S.Binary()),
    Field('is_validator', bool, if_missing=False),
    Field('_admin', bool, if_missing=False))

class Client(object):

    def regenerate_key(self, strength=2048):
        private = RSA.generate(strength)
        self.raw_public_key=bson.Binary(private.publickey().exportKey())
        return private
        
    @classmethod
    def generate(cls, principal, name=None, admin=False, strength=2048,
                 private_key=None):
        from .m_account import Account
        from .m_auth import User
        if private_key is None:
            private = RSA.generate(strength)
        else:
            private = private_key
        kwargs = dict(
            name=name,
            _admin=admin,
            raw_public_key=bson.Binary(private.publickey().exportKey()))
        if isinstance(principal, Account):
            if name is None:
                kwargs['name'] = principal.shortname + '-validator'
                kwargs['is_validator'] = True
            kwargs['account_id'] = principal._id
        elif isinstance(principal, User):
            if name is None:
                kwargs['name'] = principal.username
            kwargs.update(
                user_id=principal._id,
                account_id=principal.account_id)
        else:
            raise ValueError, 'Must specify either account or user as principal'
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
        self._admin = d['admin']
        if d.get('private_key'):
            key = self.regenerate_key()
            result['private_key'] = key.exportKey()
        return result

    @LazyProperty
    def key(self):
        return RSA.importKey(self.raw_public_key)

    @LazyProperty
    def admin(self):
        if self.user:
            return self.account.allow_access('admin', user=self.user)
        return self._admin

    def url(self, request):
        return request.relative_url(
            '/clients/' + self.name)

    @LazyProperty
    def principal(self):
        if self.user:
            return self.user
        return self.account

orm_session.mapper(Client, client, properties=dict(
        user_id=ForeignIdProperty('User'),
        account_id=ForeignIdProperty('Account'),
        user=RelationProperty('User'),
        account=RelationProperty('Account')))

Mapper.compile_all()
