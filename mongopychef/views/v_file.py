import logging

from pyramid.response import Response
from pyramid.view import view_config

from ..resources import File
from .. import model as M

log = logging.getLogger(__name__)

@view_config(
    context=File,
    renderer='json',
    request_method='GET',
    permission='read')
def read_file(context, request):
    fp = M.chef_file.m.get_file(
        str(request.account._id) + '/' + context.checksum)
    return Response(status=200, app_iter=fp)

@view_config(
    context=File,
    renderer='json',
    request_method='PUT',
    permission='update')
def upload_file(context, request):
    fobj = M.chef_file.m.get_file(
        str(request.account._id) + '/' + context.checksum)
    sb = M.Sandbox.query.get(_id=fobj.sandbox_id)
    sb.upload(context.checksum, request.body_file)
    log.info('PUT %s', context.checksum)
    return {}

