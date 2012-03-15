import sys
from itertools import groupby

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config
from pyramid.traversal import find_resource

from ..resources import Environments
from .. import model as M
from ..lib import validators as V

@view_config(
    context=Environments,
    renderer='json',
    request_method='GET',
    permission='read')
def list_environments(context, request):
    return dict(
        (obj.name, request.resource_url(obj))
        for obj in context.find())

@view_config(
    context=Environments,
    renderer='json',
    request_method='POST',
    permission='create')
def create_environment(context, request):
    env = M.Environment(account_id=request.account._id)
    env.update(V.EnvironmentSchema().to_python(request.json_body, None))
    try:
        M.orm_session.flush(env)
    except DuplicateKeyError:
        M.orm_session.expunge(env)
        raise exc.HTTPConflict()
    return dict(uri=request.resource_url(env))

@view_config(
    context=M.Environment,
    renderer='json',
    request_method='GET',
    permission='read')
def read_environment(context, request):
    return context.__json__()

@view_config(
    context=M.Environment,
    renderer='json',
    request_method='PUT',
    permission='update')
def update_environment(context, request):
    data = V.EnvironmentSchema().to_python(request.json_body, None)
    assert data['name'] == context.name
    context.update(data)
    return context.__json__()
    
@view_config(
    context=M.Environment,
    renderer='json',
    request_method='DELETE',
    permission='delete')
def delete_environment(context, request):
    context.delete()
    return context.__json__()

@view_config(
    context=M.EnvironmentCookbooks,
    renderer='json',
    request_method='GET',
    permission='read')
def list_environment_cookbooks(context, request):
    num_versions = V.CookbookNumVersions.to_python(
        request.params, None)['num_versions']
    q = request.account.find_objects(M.CookbookVersion)
    q = q.sort('name')
    result = {}
    for name, versions in groupby(q, key=lambda cb:cb.cookbook_name):
        cookbook = find_resource(request.root, 'cookbooks/' + name)
        versions = sorted(versions, key=lambda cb:cb.version_vector, reverse=True)
        versions = list(context.environment.filter_versions(name, versions))
        versions = versions[:num_versions]
        versions = map(cookbook.decorate_child, versions)
        result[name] = dict(
            url=request.resource_url(cookbook),
            versions=[
                dict(url=request.resource_url(cb), version=cb.version)
                for cb in versions ])
    return result

@view_config(
    context=M.EnvironmentCookbook,
    renderer='json',
    request_method='GET',
    permission='read')
def read_environment_cookbook(context, request):
    num_versions = V.CookbookNumVersions.to_python(
        request.params, None)['num_versions']
    cookbook = find_resource(request.root, 'cookbooks/' + context.name)
    versions = request.account.find_objects(
        M.CookbookVersion, dict(cookbook_name=context.name)).all()
    if not versions:
        raise exc.HTTPNotFound()
    versions = sorted(versions, key=lambda cb:cb.version_vector, reverse=True)
    versions = list(context.environment.filter_versions(context.name, versions))
    versions = versions[:num_versions]
    versions = map(cookbook.decorate_child, versions)
    return {
        context.name: dict(
            url=request.resource_url(cookbook),
            versions=[
                dict(url=request.resource_url(cb), version=cb.version)
                for cb in versions ]) }

@view_config(
    context=M.EnvironmentCookbookVersions,
    renderer='json',
    request_method='POST',
    permission='read')
def get_cookbook_versions(context, request):
    data = V.EnvironmentCookbookVersionsSchema.to_python(
        request.json_body, None)
    result = context.environment.get_cookbook_versions(data['run_list'])
    return result


    
