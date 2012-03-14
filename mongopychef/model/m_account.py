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

    @classmethod
    def bootstrap(self, shortname):
        '''Create an account and its groups'''
        from .m_auth import Group
        a = Account(
            name=shortname.title(),
            shortname=shortname,
            plan_id=None)
        admins = Group(
            account_id=a._id,
            name='Administrators',
            permissions=['view', 'deploy', 'admin'])
        engineers = Group(
            account_id=a._id,
            name='Engineers',
            permissions=['view', 'deploy'])
        users = Group(
            account_id=a._id,
            name='Users',
            permissions=['view'])
        return a, (admins, engineers, users)

    def get_object(self, cls, **kwargs):
        return cls.query.get(account_id=self._id, **kwargs)

    def find_objects(self, cls, *args, **kwargs):
        if len(args) == 0: args = ({},)
        args[0]['account_id'] = self._id
        return cls.query.find(*args, **kwargs)

    def allow_access(self, permission, user):
        from .m_auth import Group
        match= Group.query.get(
            account_id=self._id,
            permissions=permission,
            user_ids=user._id)
        return bool(match)

    def add_user(self, username, groups=None, display_name=None, **kw):
        from .m_auth import User
        if display_name is None: display_name = username.title()
        if groups is None: groups = []
        u = User(
            account_id=self._id,
            username=username,
            display_name=display_name,
            **kw)
        for g in groups:
            g.user_ids.append(u._id)
        return u

orm_session.mapper(Account, account, properties=dict(
        users=RelationProperty('User'),
        groups=RelationProperty('Group')))

Mapper.compile_all()
