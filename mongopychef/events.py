import json
import logging
import binascii

from pyramid.events import NewRequest, ContextFound, subscriber

from chef.auth import canonical_request, canonical_path, sha1_base64

from . import model as M

log = logging.getLogger(__name__)

@subscriber(ContextFound)
def translate_json(event):
    req = event.request
    accept = req.accept
    if accept.header_value == 'application/json':
        if not req.body:
            req.json = None
            return
        try:
            req.json = json.loads(req.body)
        except ValueError:
            log.exception('Invalid json')
            raise

@subscriber(NewRequest)
def authorize_request(event):
    req = event.request
    try:
        userid = req.headers['X-Ops-Userid']
        creq = canonical_request(
            req.method,
            canonical_path(req.path_info),
            req.headers['X-Ops-Content-Hash'],
            req.headers['X-Ops-Timestamp'],
            userid)
        assert sha1_base64(req.body) == req.headers['X-Ops-Content-Hash'], (
            'Bad body hash')
        client = M.Client.query.get(name=userid)
        if client is None:
            return
        sig_hdrs = [
            (k,v) for k,v in req.headers.items()
            if k.startswith('X-Ops-Authorization-') ]
        sig_hdrs = [
            (int(k.rsplit('-', 1)[-1]), v)
            for k,v in sig_hdrs ]
        sig_hdrs = sorted(sig_hdrs)
        b64_sig = ''.join(v for k,v in sig_hdrs)
        signature = binascii.a2b_base64(b64_sig)
        if _signature_is_valid(client.key, signature, creq):
            if client.user:
                req.environ['REMOTE_USER'] = client.user.username
            else:
                req.environ['REMOTE_USER'] = userid
            req.environ['REMOTE_ACCOUNT'] = client.account
            req.environ['CLIENT'] = client
            req.environ['REMOTE_USER'] = client
            req.client = client
            req.account = client.account
    except KeyError:
        pass
    except:
        log.exception('Error in authorize_request')
        pass

def _signature_is_valid(pubkey, signature, message):
    message_with_padding = pubkey.encrypt(signature,'')[0]
    padding, signed_message = message_with_padding.split('\x00')
    return message == signed_message
