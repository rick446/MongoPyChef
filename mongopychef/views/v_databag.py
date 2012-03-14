from json import dumps

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Databags
from .. import model as M
from ..lib import validators as V

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

@view_config(
    context=M.Databag,
    renderer='json',
    request_method='GET',
    permission='read')
def read_databag(context, request):
    return dict(
        (dbi.id, dbi.url(request))
        for dbi in context.databag.items)

@view_config(
    context=M.Databag,
    renderer='json',
    request_method='POST',
    permission='create')
def create_databag_item(context, request):
    data = V.DatabagItemSchema.to_python(request.json, None)
    raw_data = data['raw_data']
    dbi = context.databag.create_item(raw_data['id'], data=dumps(raw_data))
    try:
        M.orm_session.flush(dbi)
    except DuplicateKeyError:
        raise exc.HTTPConflict()
    return dict(uri=dbi.url(request))

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='GET',
    permission='read')
def read_databag_item(context, request):
    return context.item.__json__()

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_databag_item(context, request):
    data = V.DatabagItemSchema.to_python(request.json, None)
    raw_data = data['raw_data']
    assert raw_data['_id'] == context.item.id
    context.item.data = dumps(raw_data)
    return context.item.data

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_databag_item(context, request):
    context.item.delete()
    return context.item.data




