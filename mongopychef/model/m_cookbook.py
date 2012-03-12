import logging

from ming import collection, Field, Index
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty
from ming.utils import LazyProperty

from .m_session import doc_session, orm_session
from .m_sandbox import CookbookFile

log = logging.getLogger(__name__)

cookbook_version = collection(
    'chef.cookbook_version', doc_session,
    Field('_id', S.ObjectId()),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('name', str),
    Field('version', str),
    Field('cookbook_name', str),
    Field('metadata', None),
    Field('definitions', [ CookbookFile ]),
    Field('attributes', [ CookbookFile ]),
    Field('files', [ CookbookFile ]),
    Field('providers', [ CookbookFile ]),
    Field('resources', [ CookbookFile ]),
    Field('templates', [ CookbookFile ]),
    Field('recipes', [ CookbookFile ]),
    Field('root_files', [ CookbookFile ]),
    Field('libraries', [ CookbookFile ]),
    Index('account_id', 'cookbook_name', 'version', unique=True))

class CookbookVersion(object):

    @LazyProperty
    def version_vector(self):
        return tuple(int(x) for x in self.version.split('.'))

    @classmethod
    def cookbook_url(cls, name):
        return request.relative_url(
            config.chef_api_root + '/cookbooks/' + name)

    def url(self):
        return self.cookbook_url(self.name) + '/' + self.version

    def __json__(self):
        return dict(
            json_class='Chef::CookbookVersion',
            chef_type='cookbook_version',
            name=self.name,
            version=self.version,
            cookbook_name=self.cookbook_name,
            metadata=self.metadata,
            definitions=self.definitions,
            attributes=self.attributes,
            files=self.files,
            providers=self.providers,
            templates=self.templates,
            recipes=self.recipes,
            resources=self.resources,
            root_files=self.root_files,
            libraries=self.libraries)

    def update(self, args):
        self.cookbook_name = args['cookbook_name']
        self.metadata = args['metadata']
        self.definitions = args['definitions']
        self.attributes = args['attributes']
        self.files = args['files']
        self.providers = args['providers']
        self.templates = args['templates']
        self.recipes = args['recipes']
        self.resources = args['resources']
        self.root_files = args['root_files']
        self.libraries=args['libraries']

orm_session.mapper(CookbookVersion, cookbook_version, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))

