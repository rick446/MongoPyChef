from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Nodes, Node
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Nodes,
    renderer='json',
    request_method='GET',
    permission='read')
def list_nodes(request):
    return dict(
        (n.name, n.url(request))
        for n in M.Node.query.find(dict(
                account_id=request.account._id)))

@view_config(
    context=Nodes,
    renderer='json',
    request_method='POST',
    permission='create')
def create_node(request):
    n = M.Node(account_id=request.account._id)
    n.update(V.NodeSchema().to_python(request.json, None))
    try:
        M.orm_session.flush(n)
    except DuplicateKeyError:
        M.orm_session.expunge(n)
        raise exc.HTTPConflict()
    return dict(uri=n.url(request))

@view_config(
    context=Node,
    renderer='json',
    request_method='GET',
    permission='read')
def get_node(context, request):
    return context.node.__json__()

@view_config(
    context=Node,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_node(context, request):
    assert request.json['name'] == context.node.name
    context.node.update(V.NodeSchema().to_python(request.json, None))
    return context.node.__json__()

@view_config(
    context=Node,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_node(context, request):
    context.node.delete()
    return context.node.__json__()

