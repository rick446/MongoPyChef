import sys
from itertools import groupby
from json import dumps

from webob import exc
from pymongo.errors import DuplicateKeyError

from pyramid.view import view_config

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
    num_versions = request.params.get('num_versions', '1')
    if num_versions == 'all': num_versions = sys.maxint
    num_versions = int(num_versions)
    q = request.account.find_objects(M.CookbookVersion)
    q = q.sort('name')
    result = {}
    for name, cookbooks in groupby(q, key=lambda cb:cb.name):
        cookbooks = sorted(cookbooks, key=lambda cb:cb.version_vector)
        cookbooks = list(context.environment.filter_cookbooks(name, cookbooks))
        cookbooks = cookbooks[:num_versions]
        result[name] = dict(
            url=M.CookbookVersion.cookbook_url(request, name),
            versions=[
                dict(url=cb.url(request), version=cb.version)
                for cb in cookbooks ])
    return result

@view_config(
    context=M.EnvironmentCookbook,
    renderer='json',
    request_method='GET',
    permission='read')
def read_environment_cookbook(context, request):
    num_versions = request.params.get('num_versions', '1')
    if num_versions == 'all': num_versions = sys.maxint
    num_versions = int(num_versions)
    cookbooks = request.account.find_objects(
        M.CookbookVersion, name=context.name).all()
    if not cookbooks:
        raise exc.HTTPNotFound()
    cookbooks = sorted(cookbooks, key=lambda cb:cb.version_vector)
    cookbooks = list(context.environment.filter_cookbooks(context.name, cookbooks))
    cookbooks = cookbooks[:num_versions]
    return dict(
        name=dict(
            url=M.CookbookVersion.cookbook_url(request, context.name),
            versions=[
                dict(url=cb.url(), version=cb.version)
                for cb in cookbooks ]))

@view_config(
    context=M.EnvironmentCookbookVersions,
    renderer='json',
    request_method='POST',
    permission='read')
def get_cookbook_versions(context, request):
    if context.environment is None:
        raise exc.HTTPNotFound()
    data = V.EnvironmentCookbookVersionsSchema.to_python(request.json_body, None)
    result = context.environment.get_cookbook_versions(data['run_list'])
    return result


    
