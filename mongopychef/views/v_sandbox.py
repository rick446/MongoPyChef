from pyramid.view import view_config

from ..resources import Sandboxes
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Sandboxes,
    renderer='json',
    request_method='POST',
    permission='add')
def create_sandbox(context, request):
    data = V.SandboxSchema.to_python(request.json)
    sandbox = context.new_object(checksums=data['checksums'].keys())
    response = sandbox.initialize(request)
    return dict(
        uri=request.resource_url(sandbox),
        checksums=response)

@view_config(
    context=M.Sandbox,
    renderer='json',
    request_method='PUT',
    permission='update')
def close_sandbox(context, request):
    context.close()
    return dict(is_completed=True)

