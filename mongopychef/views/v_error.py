import json

from webob import exc

from pyramid.view import view_config
from pyramid.exceptions import Forbidden

@view_config(context=exc.HTTPError)
@view_config(context=Forbidden)
def on_error(exc, request):
    exc.body = json.dumps(dict(
        status=exc.status))
    return exc

