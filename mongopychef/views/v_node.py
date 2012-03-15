from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Nodes
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Nodes,
    renderer='json',
    request_method='GET',
    permission='read')
def list_nodes(context, request):
    return dict(
        (n.name, request.resource_url(n)) for n in context.find())

@view_config(
    context=Nodes,
    renderer='json',
    request_method='POST',
    permission='create')
def create_node(context, request):
    data = V.NodeSchema().to_python(request.json_body, None)
    n = context.new_object(name=data['name'])
    n.update(data)
    try:
        M.orm_session.flush(n)
    except DuplicateKeyError:
        M.orm_session.expunge(n)
        raise exc.HTTPConflict()
    return dict(uri=request.resource_url(n))

@view_config(
    context=M.Node,
    renderer='json',
    request_method='GET',
    permission='read')
def get_node(context, request):
    return context.__json__()

@view_config(
    context=M.Node,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_node(context, request):
    assert request.json_body['name'] == context.name
    context.update(V.NodeSchema().to_python(request.json_body, None))
    return context.__json__()

@view_config(
    context=M.Node,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_node(context, request):
    context.delete()
    return context.__json__()

