from itertools import groupby

from webob import exc

from pyramid.view import view_config
from pyramid.traversal import find_resource

from ..resources import Cookbooks, Cookbook
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Cookbooks,
    renderer='json',
    request_method='GET',
    permission='read')
def list_cookbooks(context, request):
    num_versions = V.CookbookNumVersions.to_python(
        request.params, None)['num_versions']
    q = M.CookbookVersion.query.find(dict(
            account_id=request.account._id))
    q = q.sort('name')
    result = {}
    for name, versions in groupby(q, key=lambda cb:cb.cookbook_name):
        cookbook = find_resource(context, name)
        versions = sorted(versions, key=lambda cb:cb.version_vector)
        versions = versions[:num_versions]
        versions = map(cookbook.decorate_child, versions)
        result[name] = dict(
            url=request.resource_url(context, name, ''),
            versions=[
                dict(url=request.resource_url(cb), version=cb.version)
                for cb in versions ])
    return result

@view_config(
    context=Cookbook,
    renderer='json',
    request_method='GET',
    permission='read')
def view_cookbook(context, request):
    num_versions = V.CookbookNumVersions.to_python(
        request.params, None)['num_versions']
    versions = context.find(dict(
            cookbook_name=context.name)).all()
    versions = M.CookbookVersion.query.find(dict(
            account_id=request.account._id,
            cookbook_name=context.name)).all()
    if not versions:
        raise exc.HTTPNotFound()
    versions = sorted(versions, key=lambda cb:cb.version_vector)
    versions = versions[:num_versions]
    versions = map(context.decorate_child, versions)
    return {
        context.name: dict(
            url=request.resource_url(context),
            versions=[
                dict(url=request.resource_url(cb), version=cb.version)
                for cb in versions ]) }

@view_config(
    context=M.CookbookVersion,
    renderer='json',
    request_method='GET',
    permission='read')
def view_cookbook_version(context, request):
    return context.__json__()

@view_config(
    context=M.CookbookVersion,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_cookbook_version(context, request):
    context.update(V.CookbookVersionSchema().to_python(
            request.json_body, None))
    return {}

@view_config(
    context=M.CookbookVersion,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_cookbook_version(context, request):
    context.delete()
    return {}


