import logging

from ming import collection, Field
from ming import schema as S
from ming.odm import RelationProperty
from ming.odm import Mapper

from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

account = collection(
    'account', doc_session,
    Field('_id', S.ObjectId()),
    Field('shortname', str, unique=True),
    Field('name', str))

class Account(object):
    __parent__ = None
    __name__ = None

    @classmethod
    def bootstrap(self, shortname):
        '''Create an account and its groups'''
        a = Account(
            name=shortname.title(),
            shortname=shortname,
            plan_id=None)
        return a

    def get_object(self, cls, **kwargs):
        return cls.query.get(account_id=self._id, **kwargs)

    def new_object(self, cls, **kwargs):
        return cls(account_id=self._id, **kwargs)

    def find_objects(self, cls, *args, **kwargs):
        if len(args) == 0: args = ({},)
        args[0]['account_id'] = self._id
        return cls.query.find(*args, **kwargs)

    def allow_access(self, client, permission):
        return client.account == self

orm_session.mapper(Account, account)

Mapper.compile_all()
