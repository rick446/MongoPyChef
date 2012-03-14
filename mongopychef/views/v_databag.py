from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Databags, Databag, DatabagItem
from .. import model as M

@view_config(
    context=Databags,
    renderer='json',
    request_method='GET',
    permission='read')
def list_databags(context, request):
    return dict(
        (obj.name, obj.url(request))
        for obj in request.account.find_objects(M.Client))

@view_config(
    context=Databags,
    renderer='json',
    request_method='POST',
    permission='add')
def create_databag(request):
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



