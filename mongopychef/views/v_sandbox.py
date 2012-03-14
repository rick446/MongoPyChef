from pyramid.view import view_config

from ..resources import Sandboxes, Sandbox
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Sandboxes,
    renderer='json',
    request_method='POST',
    permission='add')
def create_sandbox(context, request):
    data = V.SandboxSchema.to_python(request.json)
    sandbox, response = M.Sandbox.create(
        request.account,  data['checksums'].keys())
    return dict(
        uri=sandbox.url(request),
        checksums=response)

@view_config(
    context=Sandbox,
    renderer='json',
    request_method='PUT',
    permission='update')
def close_sandbox(context, request):
    context.sandbox.close()
    return dict(is_completed=True)
