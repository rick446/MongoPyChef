from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Roles, Role
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Roles,
    renderer='json',
    request_method='GET',
    permission='read')
def list_roles(request):
    return dict(
        (n.name, n.url(request))
        for n in M.Role.query.find(dict(
                account_id=request.account._id)))

@view_config(
    context=Roles,
    renderer='json',
    request_method='POST',
    permission='create')
def create_role(request):
    n = M.Role(account_id=request.account._id)
    n.update(V.RoleSchema().to_python(request.json, None))
    try:
        M.orm_session.flush(n)
    except DuplicateKeyError:
        M.orm_session.expunge(n)
        raise exc.HTTPConflict()
    return dict(uri=n.url(request))

@view_config(
    context=Role,
    renderer='json',
    request_method='GET',
    permission='read')
def get_role(context, request):
    return context.role.__json__()

@view_config(
    context=Role,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_role(context, request):
    data = V.RoleSchema().to_python(request.json, None)
    assert data['name'] == context.role.name
    context.role.update(data)
    return context.role.__json__()

@view_config(
    context=Role,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_role(context, request):
    context.role.delete()
    return context.role.__json__()

