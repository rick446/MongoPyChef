from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Clients
from .. import model as M
from .. import security

@view_config(
    context=Clients,
    renderer='json',
    request_method='GET',
    permission='read')
def list_clients(context, request):
    return dict(
        (cli.name, request.resource_url(cli)) for cli in context.find())

@view_config(context=Clients,
             renderer='json',
             request_method='POST',
             permission='create')
def create_client(context, request):
    cli, key = M.Client.generate(
        security.get_account(request),
        strength=request.registry.settings.key_strength,
        **request.json_body)
    cli.__parent__ = context
    try:
        M.orm_session.flush(cli)
    except DuplicateKeyError:
        M.orm_session.expunge(cli)
        raise exc.HTTPConflict()
    return dict(
        uri=request.resource_url(cli),
        private_key=key.exportKey())

@view_config(
    context=M.Client,
    renderer='json',
    request_method='GET',
    permission='read')
def get_client(context, request):
    client = security.get_client(request)
    if not client.admin and context != client:
        raise exc.HTTPForbidden()
    return context.__json__()

@view_config(
    context=M.Client,
    renderer='json',
    request_method='PUT',
    permission='update')
def put_client(context, request):
    return context.update(request.json_body)

@view_config(
    context=M.Client,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_client(context, request):
    context.delete()
    return {}

