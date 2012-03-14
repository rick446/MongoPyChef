import logging

from pyramid.response import Response
from pyramid.view import view_config

from .. import model as M

log = logging.getLogger(__name__)

@view_config(
    context=M.ChefFile,
    renderer='json',
    request_method='GET',
    permission='read')
def read_file(context, request):
    fp = M.chef_file.m.get_file(context._id)
    return Response(status=200, app_iter=fp)

@view_config(
    context=M.ChefFile,
    renderer='json',
    request_method='PUT',
    permission='update')
def upload_file(context, request):
    context.upload(request.body_file)
    log.info('PUT %s', context.md5)
    return {}

