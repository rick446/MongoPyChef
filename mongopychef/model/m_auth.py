import logging
from datetime import datetime

import bcrypt
from pyramid.threadlocal import get_current_registry

from ming import collection, Field
from ming import schema as S
from ming.orm import ForeignIdProperty, RelationProperty
from ming.utils import LazyProperty

from .m_session import doc_session, orm_session

log = logging.getLogger(__name__)

user = collection(
    'user', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('created', datetime, if_missing=datetime.utcnow),
    Field('username', str),
    Field('email', str),
    Field('password', str),
    Field('display_name', str))

group = collection(
    'group', doc_session,
    Field('_id', S.ObjectId()),
    Field('created', datetime, if_missing=datetime.utcnow),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('site_ids', [ S.ObjectId(if_missing=None) ]),  #for site-local groups
    Field('name', str),
    Field('user_ids', [ S.ObjectId(if_missing=None) ]),
    Field('permissions', [ str ]))

def password_policy(value, state):
    from formencode import Invalid
    if len(value['newpw']) < 3:
        raise Invalid('Password too short', value, state)
    if value['oldpw'] == value['newpw']:
        raise Invalid(
            'Password cannot be the same as previous password',
            value, state)

class User(object):

    def set_password(self, value):
        value = bcrypt.hashpw(
            value, bcrypt.gensalt(config.bcrypt_log_rounds))
        self.password = value

    def check_password(self, pw):
        valid = bcrypt.hashpw(pw, self.password) == self.password
        if not self.password: valid = False
        return valid

    @LazyProperty
    def groups(self):
        return Group.query.find(dict(
                user_ids=self._id)).all()

    def set_groups(self, groups):
        old_group_ids = set(g._id for g in self.groups)
        new_group_ids = set(g._id for g in groups)
        add_group_ids = new_group_ids - old_group_ids
        rem_group_ids = old_group_ids - new_group_ids
        for gid in add_group_ids:
            Group.query.get(_id=gid).user_ids.append(self._id)
        for gid in rem_group_ids:
            Group.query.get(_id=gid).user_ids.remove(self._id)

class Group(object):

    @LazyProperty
    def users(self):
        return User.query.find(dict(
                _id={'$in':self.user_ids})).all()

    @LazyProperty
    def sites(self):
        from .m_release import Site
        return Site.query.find(dict(
                _id={'$in':self.site_ids})).all()

    def set_users(self, users):
        self.user_ids = [ u._id for u in users ]

    def contains_user(self, user):
        if user is None: uid = None
        else: uid = user._id
        return uid in self.user_ids

orm_session.mapper(User, user, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))
orm_session.mapper(Group, group, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))
