import json

from webob import exc
from formencode import Invalid

from pyramid.view import view_config
from pyramid.exceptions import Forbidden

@view_config(context=exc.HTTPError)
@view_config(context=Forbidden)
def on_error(exception, request):
    exception.body = json.dumps(dict(
        status=exception.status))
    return exception

@view_config(context=Invalid)
def on_invalid(exception, request):
    err = exc.HTTPClientError()
    err.body = json.dumps(dict(
        status='400',
        detail=exception.unpack_errors()))
    return err
