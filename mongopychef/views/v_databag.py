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
        (obj.name, request.resource_url(obj)) for obj in context.find())

@view_config(
    context=Databags,
    renderer='json',
    request_method='POST',
    permission='add')
def create_databag(context, request):
    data = V.DatabagSchema.to_python(request.json, None)
    bag = context.new_object(name=data['name'])
    try:
        M.orm_session.flush(bag)
    except DuplicateKeyError:
        M.orm_session.expunge(bag)
        raise exc.HTTPConflict()
    return dict(uri=request.resource_url(bag))

@view_config(
    context=M.Databag,
    renderer='json',
    request_method='GET',
    permission='read')
def read_databag(context, request):
    items = map(context.decorate_child, context.items)
    return dict(
        (dbi.id, request.resource_url(dbi)) for dbi in items)

@view_config(
    context=M.Databag,
    renderer='json',
    request_method='POST',
    permission='create')
def create_databag_item(context, request):
    data = V.DatabagItemSchema.to_python(request.json, None)
    raw_data = data['raw_data']
    dbi = context.new_object(**raw_data)
    try:
        M.orm_session.flush(dbi)
    except DuplicateKeyError:
        M.orm_session.expunge(dbi)
        raise exc.HTTPConflict()
    return dict(uri=request.resource_url(dbi))

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='GET',
    permission='read')
def read_databag_item(context, request):
    return context.__json__()

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_databag_item(context, request):
    data = V.DatabagItemSchema.to_python(request.json, None)
    raw_data = data['raw_data']
    assert raw_data['id'] == context.id
    context.data = dumps(raw_data)
    return context.__json__()

@view_config(
    context=M.DatabagItem,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_databag_item(context, request):
    context.delete()
    return context.__json__()




