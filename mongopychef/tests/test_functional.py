import urllib2
from hashlib import md5
from cStringIO import StringIO
from unittest import TestCase

import chef
import webtest
from Crypto.PublicKey import RSA

from pyramid import testing

from mongopychef import main
from mongopychef import model as M

WEAK=1536

user_1_key = RSA.generate(WEAK)
user_2_key = RSA.generate(WEAK)
user_3_key = RSA.generate(WEAK)
validator_1_key = RSA.generate(WEAK)
validator_2_key = RSA.generate(WEAK)

class _TestUrlLibHandler(urllib2.BaseHandler):

    def __init__(self, app, expect_errors=None):
        self.app = app
        self.expect_errors = expect_errors

    def test_open(self, req):
        full_url = req.get_full_url()
        
        headers = req.header_items()
        data = req.get_data()
        environ = dict(REQUEST_METHOD=req.get_method())
        if data is not None:
            environ['wsgi.input'] = StringIO(data)
        result = self.app.request(
                full_url.replace('test://', 'http://').encode('utf-8'),
                headers=dict(headers),
                environ=environ,
                expect_errors=self.expect_errors)
        result = urllib2.addinfourl(
            StringIO(result.unicode_body.encode('utf-8')),
            result.headers,
            full_url)
        return result

def expect_errors(errors):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            urllib2.install_opener(
                urllib2.build_opener(
                    _TestUrlLibHandler(
                        self.app,
                        expect_errors=errors)))
            return func(self, *args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

class ChefTest(TestCase):

    def setUp(self):
        app = main(
            {}, 
            **{'debug_authorization': 'false',
               'debug_notfound': 'false',
               'debug_routematch': 'false',
               'debug_templates': 'true',
               'default_locale_name': 'en',
               'ming.chef.database': 'chef',
               'ming.chef.master': 'mim:///',
               'reload_templates': 'true',
               'key_strength': 1536,
               'session_secret': 'itsasecret'}
            )
        self.app = webtest.TestApp(app)
        
        urllib2.install_opener(
            urllib2.build_opener(_TestUrlLibHandler(self.app)))
        self.bootstrap_data()
        self.chef_1_validator = chef.ChefAPI(
            'test://test',
            key=StringIO(validator_1_key.exportKey()),
            client='test-1-validator',
            version='0.10')
        self.chef_2_validator = chef.ChefAPI(
            'test://test',
            key=StringIO(validator_1_key.exportKey()),
            client='test-2-validator',
            version='0.10')
        self.chef_user_1 = chef.ChefAPI(
            'test://test',
            key=StringIO(user_1_key.exportKey()),
            client='test-user-1',
            version='0.10')
        self.chef_user_2 = chef.ChefAPI(
            'test://test',
            key=StringIO(user_1_key.exportKey()),
            client='test-user-2',
            version='0.10')
        self.chef_user_3 = chef.ChefAPI(
            'test://test',
            key=StringIO(user_3_key.exportKey()),
            client='test-user-3',
            version='0.10')

    def tearDown(self):
        testing.tearDown()

    def bootstrap_data(self):
        M.doc_session.db.connection.clear_all()
        M.orm_session.clear()
        a1 = M.Account.bootstrap('test-1')
        a2 = M.Account.bootstrap('test-2')
        M.orm_session.flush()
        M.Client.generate(a1, private_key=validator_1_key, admin=True)
        M.Client.generate(a2, private_key=validator_2_key, admin=True)
        M.Client.generate(a1, 'test-user-1', admin=False,
                          private_key=user_1_key)
        M.Client.generate(a2, 'test-user-2', admin=False,
                          private_key=user_2_key)
        M.Client.generate(a2, 'test-user-3', admin=True,
                          private_key=user_3_key)
        M.orm_session.flush()
        M.orm_session.clear()
        self.a1 = a1
        self.a2 = a2

class TestClient(ChefTest):
    clients_1 = {
        'test-1-validator':'http://test/clients/test-1-validator/',
        'test-user-1':'http://test/clients/test-user-1/',
        }
    clients_2 = {
        'test-2-validator':'http://test/clients/test-2-validator/',
        'test-user-2':'http://test/clients/test-user-2/'
        }

    def test_list(self):
        self.assertEqual(
            self.chef_1_validator.api_request('GET', '/clients'),
            self.clients_1)
        self.assertEqual(
            self.chef_user_1.api_request('GET', '/clients'),
            self.clients_1)
        self.assertEqual(
            self.chef_1_validator.api_request('GET', '/clients'),
            self.clients_1)
        self.assertEqual(
            self.chef_user_1.api_request('GET', '/clients'),
            self.clients_1)

    def test_create(self):
        result = self.chef_1_validator.api_request(
            'POST', '/clients', data=dict(
                    name='rick', admin=True))
        self.assertEqual(result['uri'], 'http://test/clients/rick/')
        self.assert_(1270 < len(result['private_key']) < 1300)

    @expect_errors([409])
    def test_create_duplicate(self):
        result = self.chef_1_validator.api_request(
            'POST', '/clients', data=dict(
                    name='test-user-1', admin=True))
        assert result['status'].startswith('409')

    def test_get_ok(self):
        result = self.chef_1_validator.api_request(
            'GET', '/clients/test-user-1')
        assert result['name'] == 'test-user-1'
        assert result['admin'] == False
        assert result['public_key']
        result = self.chef_1_validator.api_request(
            'GET', '/clients/test-1-validator')
        assert result['name'] == 'test-1-validator'
        assert result['admin'] == True
        assert result['public_key']
        result = self.chef_user_1.api_request(
            'GET', '/clients/test-user-1')
        assert result['name'] == 'test-user-1'
        assert result['admin'] == False
        assert result['public_key']
        # with self.assertRaises(

    @expect_errors([403])
    def test_get_403(self):
        result = self.chef_user_1.api_request(
            'GET', '/clients/test-1-validator')
        self.assert_(result['status'].startswith('403'))

    @expect_errors([404])
    def test_get_other_account(self):
        result = self.chef_1_validator.api_request(
            'GET', '/clients/test-user-2')
        self.assert_(result['status'].startswith('404'))

    @expect_errors([404])
    def test_get_404(self):
        result = self.chef_user_1.api_request(
            'GET', '/clients/does-not-exist')
        self.assert_(result['status'].startswith('404'))

    def test_put(self):
        result = self.chef_1_validator.api_request(
            'PUT', '/clients/test-user-1', data=dict(
                name='test-user-1',
                admin=True))
        assert 'private_key' not in result
        result = self.chef_1_validator.api_request(
            'PUT', '/clients/test-user-1', data=dict(
                name='test-user-1',
                admin=True,
                private_key=True))
        assert 'private_key' in result

    def test_delete_ok(self): 
        result = self.chef_1_validator.api_request(
            'DELETE', '/clients/test-user-1')
        result = self.chef_1_validator.api_request('GET', '/clients')
        assert len(result) == 1, result

    @expect_errors([403])
    def test_delete_self(self):
        result = self.chef_user_1.api_request(
            'DELETE', '/clients/test-user-1')
        self.assert_(result['status'].startswith('403'))
        result = self.chef_1_validator.api_request('GET', '/clients')
        assert len(result) == 2

    @expect_errors([403])
    def test_delete_validator(self):
        result = self.chef_user_3.api_request(
            'DELETE', '/clients/test-2-validator')
        self.assert_(result['status'].startswith('403'))
        result = self.chef_1_validator.api_request('GET', '/clients')
        assert len(result) == 2

class TestNode(ChefTest):
    
    def setUp(self):
        super(TestNode, self).setUp()
        M.Node(account_id=self.a1._id, name='test-node')
        M.orm_session.flush()
        M.orm_session.clear()

    def test_list(self):
        result = self.chef_1_validator.api_request('GET', '/nodes')
        self.assertEqual(result, {
                u'test-node': u'http://test/nodes/test-node/'})

    def test_post_ok(self):
        result = self.chef_1_validator.api_request(
            'POST', '/nodes',  data=dict(
                name='foo'))
        self.assertEqual(result, {
                'uri': u'http://test/nodes/foo/'})

    @expect_errors([409])
    def test_post_duplicate(self):
        result = self.chef_1_validator.api_request(
            'POST', '/nodes',  data=dict(
                name='test-node'))
        assert result['status'].startswith('409')

    def test_get_ok(self):
        result = self.chef_1_validator.api_request(
            'GET', '/nodes/test-node')
        self.assertEqual(result, {
                u'name': u'test-node',
                u'chef_type': u'node',
                u'json_class': u'Chef::Node',
                u'chef_environment': u'_default',
                u'run_list': [],
                u'normal': {},
                u'default': {},
                u'override': {},
                u'automatic': {}})

    @expect_errors([404])
    def test_get_404(self):
        result = self.chef_1_validator.api_request(
            'GET', '/nodes/does-not-exist')
        self.assert_(result['status'].startswith('404'))
        
    def test_put_ok(self):
        result = self.chef_1_validator.api_request(
            'PUT', '/nodes/test-node', data=dict(
                name='test-node',
                normal={'a':5}))
        self.assertEqual(result, {
                u'name': u'test-node',
                u'chef_type': u'node',
                u'json_class': u'Chef::Node',
                u'chef_environment': u'_default',
                u'run_list': [],
                u'normal': {'a':5},
                u'default': {},
                u'override': {},
                u'automatic': {}})
        
    def test_delete_ok(self):
        result = self.chef_1_validator.api_request(
            'DELETE', '/nodes/test-node')
        self.assertEqual(result, {
                u'name': u'test-node',
                u'chef_type': u'node',
                u'json_class': u'Chef::Node',
                u'chef_environment': u'_default',
                u'run_list': [],
                u'normal': {},
                u'default': {},
                u'override': {},
                u'automatic': {}})

class TestDatabag(ChefTest):

    def setUp(self):
        super(TestDatabag, self).setUp()
        bag = M.Databag(account_id=self.a1._id, name='test-bag')
        bag.new_object(id='test-item', data='bar')
        M.orm_session.flush()
        M.orm_session.clear()

    def test_list_bags(self):
        result = self.chef_user_1.api_request('GET', '/data')
        self.assertEqual(result, {u'test-bag': u'http://test/data/test-bag/'})

    def test_new_bag_ok(self):
        result = self.chef_1_validator.api_request(
            'POST', '/data', data=dict(name='test-bag-2'))
        self.assertEqual(result, {
                'uri': u'http://test/data/test-bag-2/'})

    @expect_errors([409])
    def test_new_bag_duplicate(self):
        result = self.chef_1_validator.api_request(
            'POST', '/data', data=dict(name='test-bag'))
        assert result['status'].startswith('409')

    def test_get_bag_ok(self):
        result = self.chef_user_1.api_request('GET', '/data/test-bag')
        self.assertEqual(result, {
                u'test-item': u'http://test/data/test-bag/test-item/'})

    @expect_errors([404])
    def test_get_bag_404(self):
        result = self.chef_user_1.api_request('GET', '/data/test-bag-does-not-exist')
        self.assert_(result['status'].startswith('404'))

    def test_new_item_ok(self):
        result = self.chef_1_validator.api_request(
            'POST', '/data/test-bag', data=dict(
                name='test-item-2',
                raw_data={'id': 'test-item-2', 'other': 'foo'}))
        self.assertEqual(result, {
                u'uri': u'http://test/data/test-bag/test-item-2/'})

    @expect_errors([409])
    def test_new_item_duplicate(self):
        result = self.chef_1_validator.api_request(
            'POST', '/data/test-bag', data=dict(
                name='test-item',
                raw_data={'id':'test-item'}))
        assert result['status'].startswith('409')

    def test_get_item_ok(self):
        result = self.chef_user_1.api_request('GET', '/data/test-bag/test-item')
        self.assertEqual(result, {
                "data": "bar", "id": "test-item"})

    @expect_errors([404])
    def test_get_item_404(self):
        result = self.chef_user_1.api_request('GET', '/data/test-bag/does-not-exist')
        self.assert_(result['status'].startswith('404'))

    def test_put_item_ok(self):
        result = self.chef_1_validator.api_request(
            'PUT', '/data/test-bag/test-item', data=dict(
                name='test-item',
                raw_data={'id':'test-item', 'data':'baz'}))
        self.assertEqual(result, {
                "data": "baz", "id": "test-item"})

    def test_delete_item_ok(self):
        result = self.chef_1_validator.api_request(
            'DELETE', '/data/test-bag/test-item/')
        self.assertEqual(result, {
                "data": "bar", "id": "test-item"})

class TestRole(ChefTest):

    def setUp(self):
        super(TestRole, self).setUp()
        M.Role(account_id=self.a1._id, name='test-role')
        M.orm_session.flush()
        M.orm_session.clear()

    def test_list_roles(self):
        result = self.chef_user_1.api_request('GET', '/roles')
        self.assertEqual(result, {u'test-role': u'http://test/roles/test-role/'})

    def test_new_role_ok(self):
        result = self.chef_1_validator.api_request(
            'POST', '/roles', data=dict(name='test-role-2'))
        self.assertEqual(result, {
                'uri': u'http://test/roles/test-role-2/'})

    @expect_errors([409])
    def test_new_bag_duplicate(self):
        result = self.chef_1_validator.api_request(
            'POST', '/roles', data=dict(name='test-role'))
        assert result['status'].startswith('409')

    def test_get_role_ok(self):
        result = self.chef_user_1.api_request('GET', '/roles/test-role')
        self.assertEqual(result, {
                u'chef_type': u'role',
                u'default_attributes': {},
                u'description': None,
                u'env_run_lists': {},
                u'json_class': u'Chef::Role',
                u'name': u'test-role',
                u'override_attributes': {},
                u'run_list': []})

    @expect_errors([404])
    def test_get_bag_404(self):
        result = self.chef_user_1.api_request('GET', '/roles/does-not-exist')
        self.assert_(result['status'].startswith('404'))

    def test_put_role_ok(self):
        result = self.chef_1_validator.api_request(
            'PUT', '/roles/test-role', data=dict(
                name='test-role',
                description='The test role'))
        self.assertEqual(result, {
                u'chef_type': u'role',
                u'default_attributes': {},
                u'description': 'The test role',
                u'env_run_lists': {},
                u'json_class': u'Chef::Role',
                u'name': u'test-role',
                u'override_attributes': {},
                u'run_list': []})
        
    def test_delete_role_ok(self):
        result = self.chef_1_validator.api_request(
            'DELETE', '/roles/test-role')
        self.assertEqual(result, {
                u'chef_type': u'role',
                u'default_attributes': {},
                u'description': None,
                u'env_run_lists': {},
                u'json_class': u'Chef::Role',
                u'name': u'test-role',
                u'override_attributes': {},
                u'run_list': []})

class TestSandbox(ChefTest):

    def setUp(self):
        super(TestSandbox, self).setUp()
        self.file_content = 'Hello World'
        self.file_checksum = md5(self.file_content).hexdigest()
        self.file_url = 'http://test/files/%s-%s/' % (self.a1._id, self.file_checksum)
        M.orm_session.flush()
        M.orm_session.clear()

    def _create_sandbox(self):
        return self.chef_1_validator.api_request(
            'POST', '/sandboxes', data=dict(checksums={
                    self.file_checksum: None}))

    def _upload_file(self, sb):
        file_url = sb['checksums'].values()[0]['url']
        file_path = file_url[len('http://test'):]
        headers = {'accept':'application/json'}
        return self.chef_1_validator.request(
            'PUT', file_path, headers, data=self.file_content)

    def _download_file(self):
        file_path = self.file_url[len('http://test'):]
        headers = {'accept':'application/json'}
        headers = {}
        return self.chef_1_validator.request(
            'GET', file_path, headers)

    def _close_sandbox(self, sb):
        sb_path = sb['uri'][len('http://test'):]
        result = self.chef_1_validator.api_request(
            'PUT', sb_path, data=dict(is_completed=True))
        return result
        
    def test_new_sandbox_ok(self):
        result = self._create_sandbox()
        uri = result.pop('uri')
        self.assertEqual(result, {
                u'checksums': {
                    u'b10a8db164e0754105b7a99be72e3fe5': {
                        u'url': self.file_url, u'needs_upload': True}}})

    def test_close_sandbox_ok(self):
        sb = self._create_sandbox()
        self._upload_file(sb)
        self._close_sandbox(sb)

    @expect_errors([400])
    def test_close_sandbox_unfinished(self):
        sb = self._create_sandbox()
        result = self._close_sandbox(sb)
        assert result['status'].startswith('400')

    def test_new_sandbox_no_files_to_upload(self):
        self.maxDiff = None
        sb = self._create_sandbox()
        self._upload_file(sb)
        self._close_sandbox(sb)
        result = self._create_sandbox()
        uri = result.pop('uri')
        self.assertEqual(result, {
                u'checksums': {
                    u'b10a8db164e0754105b7a99be72e3fe5': {
                        u'url': self.file_url, u'needs_upload': False}}})

    def test_download_file(self):
        sb = self._create_sandbox()
        self._upload_file(sb)
        self._close_sandbox(sb)
        result = self._download_file()
        self.assertEqual(result, 'Hello World')

def create_cookbooks(account, names, versions):
    for name in names:
        for version in versions:
            account.new_object(
                M.CookbookVersion,
                name='%s-%s' % (name, version),
                cookbook_name=name,
                version=version)

class TestCookbook(ChefTest):

    def setUp(self):
        super(TestCookbook, self).setUp()
        create_cookbooks(
            self.a1, ['mpc', 'arden'], [ '1.0', '1.1', '1.2' ])
        M.orm_session.flush()
        M.orm_session.clear()

    def test_list_cookbooks_default(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks')
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [{u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'}]},
                u'mpc': {
                    u'url': u'http://test/cookbooks/mpc/',
                    u'versions': [{u'url': u'http://test/cookbooks/mpc/1.2/', u'version': u'1.2'}]}})

    def test_list_cookbooks_all(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks?num_versions=all')
        self.maxDiff=None
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'},
                        {u'url': u'http://test/cookbooks/arden/1.1/', u'version': u'1.1'},
                        {u'url': u'http://test/cookbooks/arden/1.0/', u'version': u'1.0'} ] },
                u'mpc': {
                    u'url': u'http://test/cookbooks/mpc/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/mpc/1.2/', u'version': u'1.2'},
                        {u'url': u'http://test/cookbooks/mpc/1.1/', u'version': u'1.1'},
                        {u'url': u'http://test/cookbooks/mpc/1.0/', u'version': u'1.0'} ] }
                })

    def test_view_cookbook_default(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks/arden')
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [{u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'}]}
                })

    @expect_errors([404])
    def test_view_cookbook_404(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks/does-not-exist')
        self.assert_(result['status'].startswith('404'))

    @expect_errors([404])
    def test_view_cookbook_version_404(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks/arden/2.0')
        self.assert_(result['status'].startswith('404'))

    def test_view_cookbook_all(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks/arden?num_versions=all')
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'},
                        {u'url': u'http://test/cookbooks/arden/1.1/', u'version': u'1.1'},
                        {u'url': u'http://test/cookbooks/arden/1.0/', u'version': u'1.0'},
                        ]}
                })

    def test_view_version(self):
        result = self.chef_user_1.api_request('GET', '/cookbooks/arden/1.0')
        self.assertEqual(result, {
                u'name': u'arden-1.0',
                u'cookbook_name': u'arden',
                u'version': u'1.0',
                u'chef_type': u'cookbook_version',
                u'json_class': u'Chef::CookbookVersion',
                u'templates': [],
                u'files': [],
                u'providers': [],
                u'recipes': [],
                u'libraries': [],
                u'definitions': [],
                u'root_files': [],
                u'attributes': [],
                u'resources': [],
                u'metadata': {}})

    def test_update_version(self):
        version = self.chef_1_validator.api_request('GET', '/cookbooks/arden/1.0')
        version['metadata'] = dict(a=5)
        result = self.chef_1_validator.api_request(
            'PUT', '/cookbooks/arden/1.0/',
            data=version)

    def test_delete_version(self):
        self.chef_1_validator.api_request('DELETE', '/cookbooks/arden/1.0/')
        result = self.chef_1_validator.api_request('GET', '/cookbooks/arden?num_versions=all')
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'},
                        {u'url': u'http://test/cookbooks/arden/1.1/', u'version': u'1.1'},
                        ]}
                })

class TestEnvironment(ChefTest):

    def setUp(self):
        super(TestEnvironment, self).setUp()
        self.a1.new_object(
            M.Environment, name='Test', cookbook_versions=dict(
                mpc='1.2'))
        self.a1.new_object(
            M.Environment, name='Prod', cookbook_versions=dict(
                arden='1.0',
                mpc='1.0'))
        create_cookbooks(
            self.a1, ['mpc', 'arden'], [ '1.0', '1.1', '1.2' ])
        M.orm_session.flush()
        M.orm_session.clear()

    def test_list_environ(self):
        result = self.chef_user_1.api_request('GET', '/environments')
        self.assertEqual(result, {
                u'Test': u'http://test/environments/Test/',
                u'Prod': u'http://test/environments/Prod/'})
        
    def test_create_environ_ok(self):
        result = self.chef_1_validator.api_request('POST', '/environments', data=dict(
                name='Staging'))
        result = self.chef_user_1.api_request('GET', '/environments')
        self.assertEqual(result, {
                u'Test': u'http://test/environments/Test/',
                u'Staging': u'http://test/environments/Staging/',
                u'Prod': u'http://test/environments/Prod/'})
        
    @expect_errors([409])
    def test_create_environ_dupe(self):
        result = self.chef_1_validator.api_request('POST', '/environments', data=dict(
                name='Test'))
        self.assert_(result['status'].startswith('409'))

    def test_read_environ(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test')
        self.assertEqual(result, {
                u'chef_type': u'environment',
                u'default_attributes': {},
                u'description': '',
                u'override_attributes': {},
                u'cookbook_versions': {u'mpc': u'1.2'},
                u'json_class': u'Chef::Environment',
                u'name': u'Test'})

    def test_update_environ(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test')
        result['description'] = 'The test environ'
        result = self.chef_1_validator.api_request('PUT', '/environments/Test', data=result)
        self.assertEqual(result, {
                u'chef_type': u'environment',
                u'default_attributes': {},
                u'description': 'The test environ',
                u'override_attributes': {},
                u'cookbook_versions': {u'mpc': u'1.2'},
                u'json_class': u'Chef::Environment',
                u'name': u'Test'})

    def test_delete_environ(self):
        self.chef_1_validator.api_request('DELETE', '/environments/Test')
        result = self.chef_user_1.api_request('GET', '/environments')
        self.assertEqual(result, {
                u'Prod': u'http://test/environments/Prod/'})

    def test_list_environ_cookbooks(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test/cookbooks')
        self.maxDiff=None
        self.assertEqual(result, {
                u'mpc': {
                    u'url': u'http://test/cookbooks/mpc/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/mpc/1.2/', u'version': u'1.2'}] },
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'} ]},
                })

    def test_list_environ_cookbooks_all(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test/cookbooks?num_versions=all')
        self.maxDiff=None
        self.assertEqual(result, {
                u'mpc': {
                    u'url': u'http://test/cookbooks/mpc/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/mpc/1.2/', u'version': u'1.2'}] },
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [
                        {u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'},
                        {u'url': u'http://test/cookbooks/arden/1.1/', u'version': u'1.1'},
                        {u'url': u'http://test/cookbooks/arden/1.0/', u'version': u'1.0'},
                        ]}
                })
        
    def test_view_environment_cookbook_default(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test/cookbooks/arden')
        self.assertEqual(result, {
                u'arden': {
                    u'url': u'http://test/cookbooks/arden/',
                    u'versions': [{u'url': u'http://test/cookbooks/arden/1.2/', u'version': u'1.2'}]}
                })

    @expect_errors([404])
    def test_view_cookbook_404(self):
        result = self.chef_user_1.api_request('GET', '/environments/Test/cookbooks/does-not-exist')
        self.assert_(result['status'].startswith('404'))

    def test_get_cookbook_versions(self):
        result = self.chef_user_1.api_request('POST', '/environments/Test/cookbook_versions', data=dict(
                run_list=['mpc', 'arden@1.1']))
        self.assertEqual(result, {
                u'arden': {
                    u'chef_type':u'cookbook_version',
                    u'json_class': u'Chef::CookbookVersion',
                    u'name': u'arden-1.1',
                    u'cookbook_name': u'arden',
                    u'version': u'1.1',
                    u'templates': [],
                    u'files': [],
                    u'providers': [],
                    u'recipes': [],
                    u'libraries': [],
                    u'definitions': [],
                    u'root_files': [],
                    u'attributes': [],
                    u'resources': [],
                    u'metadata': {}},
                u'mpc': {
                    u'chef_type': u'cookbook_version',
                    u'json_class': u'Chef::CookbookVersion',
                    u'name': u'mpc-1.2',
                    u'cookbook_name': u'mpc',
                    u'version': u'1.2',
                    u'templates': [],
                    u'files': [],
                    u'providers': [],
                    u'recipes': [],
                    u'libraries': [],
                    u'definitions': [],
                    u'root_files': [],
                    u'attributes': [],
                    u'resources': [],
                    u'metadata': {}}})
