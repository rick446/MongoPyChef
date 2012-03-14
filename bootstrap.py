'''Boostrap a mongopychef account

USAGE: bootstrap.py <ini file> <account_shortname> <account_name>
Returns: validtor PEM file (to stdout)
'''
import sys
import ConfigParser
from contextlib import contextmanager

from ming.odm import ThreadLocalODMSession

from mongopychef import main
from mongopychef import model as M

configfile, shortname, name = sys.argv[1:]

cp = ConfigParser.ConfigParser()
cp.read(configfile)
config_dict = dict(cp.items('app:MongoPyChef'))

app = main({},  **config_dict)

@contextmanager
def flush_context():
    ThreadLocalODMSession.close_all()
    try:
        yield
        ThreadLocalODMSession.flush_all()
    finally:
        ThreadLocalODMSession.close_all()

with flush_context():
    account, groups = M.Account.bootstrap(shortname=shortname)
    account.name = name
    client, private = M.Client.generate(account, admin=True)
    print 'Validator key saved in  %s-validator.pem' % (account.shortname)
    with open('%s-validator.pem' % account.shortname, 'wb') as fp:
        fp.write(private.exportKey())
    admin_user = M.User(account_id=account._id, username='root', display_name='Root User')
    groups[0].user_ids.append(admin_user._id)
    client, private = M.Client.generate(admin_user)
    print 'Root key saved in root.pem'
    with open('root.pem', 'wb') as fp:
        fp.write(private.exportKey())
    
    

    

