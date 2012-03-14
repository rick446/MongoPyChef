import logging

from formencode import Invalid
from pymongo.errors import DuplicateKeyError
from pyramid.traversal import find_resource

from ming import collection, Field
from ming.fs import filesystem
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session
from ..lib.util import cnonce

log = logging.getLogger(__name__)

sandbox = collection(
    'chef.sandbox', doc_session,
    Field('_id', str, if_missing=cnonce),
    Field('account_id', S.ObjectId(if_missing=None)),
    Field('checksums', [ str ]))

chef_file = filesystem(
    'chef.file', doc_session,
    Field('_id', str), # account_id-md5
    Field('needs_upload', bool, if_missing=True))

class Sandbox(ModelBase):

    @property
    def __name__(self):
        return str(self._id)

    def initialize(self, request):
        checksum_index = dict(
            (self.file_id(cs), cs)
            for cs in self.checksums)
        existing_files = self.account.find_objects(
            ChefFile,  dict(_id={'$in': checksum_index.keys()}))
        existing_files_by_id = dict(
            (f._id, f) for f in existing_files)
        response = {}
        for file_id, cs in checksum_index.items():
            f = existing_files_by_id.get(file_id, None)
            if f is None:
                try:
                    f = self.account.new_object(
                        ChefFile, _id=file_id, md5=cs)
                    orm_session.flush(f)
                except DuplicateKeyError:
                    orm_session.expunge(f)
                    f = self.account.get_object(ChefFile, _id=file_id)
            f.__parent__ = find_resource(request.root, '/files/')
            response[cs] = dict(
                url=request.resource_url(f),
                needs_upload=f.needs_upload)
        return response

    def file_id(self, checksum):
        return str(self.account_id) + '-' + checksum

    def close(self, request):
        ids = map(self.file_id, self.checksums)
        missing_files = ChefFile.query.find(dict(
                _id={'$in': ids},
                needs_upload=True)).all()
        if missing_files:
            raise Invalid(
                'Missing uploads',
                {}, None,
                error_dict=dict(
                   (request.resource_url(f), 'Missing upload')
                   for f in missing_files))
        self.delete()

class ChefFile(ModelBase):
    CHUNKSIZE=4096

    @property
    def __name__(self):
        return self._id

    def upload(self, ifp):
        fs = self.query.mapper.collection.m.fs
        fs.delete(self._id)
        with fs.new_file(_id=self._id) as ofp:
            while True:
                chunk = ifp.read(self.CHUNKSIZE)
                if chunk: ofp.write(chunk)
                else: break
        if ofp.md5 != self.md5:
            import pdb; pdb.set_trace()
            chef_file.m.fs.delete(self._id)
            raise Invalid('Invalid checksum', None, None)

orm_session.mapper(Sandbox, sandbox, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))
orm_session.mapper(ChefFile, chef_file,properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))

