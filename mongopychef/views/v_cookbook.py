from itertools import groupby

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

from ..resources import Cookbooks, Cookbook, CookbookVersion
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Cookbooks, renderer='json',
    request_method='GET', permission='view')
def list_cookbooks(context, request):
    num_versions = V.NodeSchema().to_python(
        request.params.get('num_versions', 1), None)
    q = M.CookbookVersion.query.find(dict(
            account_id=request.account._id))
    q = q.sort('name')
    result = {}
    for name, cookbooks in groupby(q, key=lambda cb:cb.name):
        cookbooks = sorted(cookbooks, key=lambda cb:cb.version_vector)
        cookbooks = cookbooks[:num_versions]
        result[name] = dict(
            url=M.CookbookVersion.cookbook_url(request, name),
            versions=[
                dict(url=cb.url(request), version=cb.version)
                for cb in cookbooks ])
    return result

@view_config(
    context=Cookbook, renderer='json',
    request_method='GET', permission='view')
def view_cookbook(context, request):
    num_versions = V.NodeSchema().to_python(
        request.params.get('num_versions', 1), None)
    cookbooks = M.CookbookVersion.query.find(dict(
            account_id=request.account._id,
            name=context.cookbook_name)).all()
    if not cookbooks:
        raise exc.HTTPNotFound()
    cookbooks = sorted(cookbooks, key=lambda cb:cb.version_vector)
    cookbooks = cookbooks[:num_versions]
    return dict(
        name=dict(
            url=M.CookbookVersion.cookbook_url(
                request, context.cookbook_name),
            versions=[
                dict(url=cb.url(), version=cb.version)
                for cb in cookbooks ]))

@view_config(
    context=CookbookVersion, renderer='json',
    request_method='GET', permission='view')
def view_cookbook_version(context, request):
    return context.cookbook_version.__json__()

@view_config(
    context=CookbookVersion, renderer='json',
    request_method='PUT', permission='edit')
def update_cookbook_version(context, request):
    M.CookbookVersion.query.remove(dict(
        account_id=request.account._id,
        name=context.cookbook_name,
        version=context.cookbook_version))
    cb = M.CookbookVersion(
        account_id=context.account._id,
        name=context.cookbook_name,
        version=context.cookbook_version)
    cb.update(V.NodeSchema().to_python(request.json, None))
    return {}

@view_config(
    context=CookbookVersion, renderer='json',
    request_method='DELETE', permission='delete')
def delete_cookbook_version(context, request):
    if context.cookbook_version is None:
        raise exc.HTTPNotFound()
    context.cookbook_version.delete()
    return {}


