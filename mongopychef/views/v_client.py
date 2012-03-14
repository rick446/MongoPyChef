from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Clients, Client
from .. import model as M

@view_config(
    context=Clients,
    renderer='json',
    request_method='GET',
    permission='read')
def list_clients(request):
    return dict(
        (cli.name, cli.url(request))
        for cli in M.Client.query.find(dict(account_id=request.account._id)))

@view_config(context=Clients,
             renderer='json',
             request_method='POST',
             permission='create')
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
    context=Client,
    renderer='json',
    request_method='GET',
    permission='read')
def get_client(context, request):
    if not request.client.admin and context.client != request.client:
        raise exc.HTTPForbidden()
    return context.client.__json__()

@view_config(
    context=Client,
    renderer='json',
    request_method='PUT',
    permission='update')
def put_client(context, request):
    cli = context.client
    return cli.update(request.json)

@view_config(
    context=Client,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_client(context, request):
    context.client.delete()
    return {}

