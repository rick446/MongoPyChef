import json

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config
from pyramid.exceptions import Forbidden

from ..resources import Clients, Client
from .. import model as M

@view_config(context=Clients, renderer='json', request_method='GET')
def list_clients(request):
    return dict(
        (cli.name, cli.url(request))
        for cli in M.Client.query.find(dict(account_id=request.client.account_id)))

@view_config(context=Clients,
             renderer='json',
             request_method='POST',
             permission='add')
def create_client(request):
    cli, key = M.Client.generate(
        request.client.principal, **request.json)
    try:
        M.orm_session.flush(cli)
    except DuplicateKeyError:
        M.orm_session.expunge(cli)
        raise exc.HTTPConflict()
    return dict(
        uri=cli.url(request),
        private_key=key.exportKey())

@view_config(
    context=Client, renderer='json', request_method='GET',
    permission='view')
def get_client(context, request):
    if not request.client.admin and context.client != request.client:
        raise exc.HTTPForbidden()
    return request.context.client.__json__()

@view_config(
    context=Client, renderer='json', request_method='PUT',
    permission='edit')
def put_client(request):
    cli = request.context.client
    return cli.update(request.json)

@view_config(context=Client, renderer='json', request_method='DELETE',
             permission='delete')
def delete_client(request):
    cli = request.context.client
    if cli == request.client:
        raise exc.HTTPForbidden()
    elif cli.is_validator:
        raise exc.HTTPForbidden()
    cli.delete()
    return {}

@view_config(context=exc.HTTPError)
@view_config(context=Forbidden)
def on_error(exc, request):
    exc.body = json.dumps(dict(
        status=exc.status))
    return exc

