from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Roles
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Roles,
    renderer='json',
    request_method='GET',
    permission='read')
def list_roles(context, request):
    return dict(
        (n.name, request.resource_url(n))
        for n in context.find())

@view_config(
    context=Roles,
    renderer='json',
    request_method='POST',
    permission='create')
def create_role(context, request):
    n = context.new_object()
    n.update(V.RoleSchema().to_python(request.json, None))
    try:
        M.orm_session.flush(n)
    except DuplicateKeyError:
        M.orm_session.expunge(n)
        raise exc.HTTPConflict()
    return dict(uri=request.resource_url(n))

@view_config(
    context=M.Role,
    renderer='json',
    request_method='GET',
    permission='read')
def get_role(context, request):
    return context.__json__()

@view_config(
    context=M.Role,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_role(context, request):
    data = V.RoleSchema().to_python(request.json, None)
    assert data['name'] == context.name
    context.update(data)
    return context.__json__()

@view_config(
    context=M.Role,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_role(context, request):
    context.delete()
    return context.__json__()

