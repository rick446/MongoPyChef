import logging

from formencode import Invalid

from ming import collection, Field
from ming.fs import filesystem
from ming import schema as S
from ming.orm import RelationProperty, ForeignIdProperty

from .m_base import ModelBase
from .m_session import doc_session, orm_session
from mongopychef.lib.util import cnonce

log = logging.getLogger(__name__)

sandbox = collection(
    'chef.sandbox', doc_session,
    Field('_id', str, if_missing=cnonce),
    Field('account_id', S.ObjectId(if_missing=None)))

chef_file = filesystem(
    'chef.file', doc_session,
    Field('_id', str), # account_id/md5
    Field('sandbox_id', str),
    Field('needs_upload', bool))

class Sandbox(ModelBase):
    CHUNKSIZE=4096

    @classmethod
    def create(cls, account, checksums):
        sb = cls(account_id=account._id)
        file_index = dict(
            (sb.file_id(cs), cs)
            for cs in checksums)
        existing_files = chef_file.m.find(
            dict(
                _id={'$in': file_index.keys()}),
            validate=False)
        existing_files_by_id = dict(
            (f._id, f) for f in existing_files)
        response = {}
        for file_id, cs in file_index.items():
            f = existing_files_by_id.get(file_id, None)
            if f is None:
                chef_file.make(dict(
                        _id=file_id,
                        sandbox_id=sb._id,
                        needs_upload=True)).m.insert()
                needs_upload=True
            elif f['needs_upload']:
                chef_file.m.update_partial(
                    dict(_id=file_id),
                    { '$set': dict(sandbox_id=sb._id, needs_upload=True) })
                needs_upload=True
            else:
                chef_file.m.update_partial(
                    dict(_id=file_id),
                    { '$set': dict(sandbox_id=sb._id, needs_upload=False) })
                needs_upload=False
            response[cs] = dict(
                url=sb.url_for(cs),
                needs_upload=needs_upload)
        return sb, response

    def file_id(self, checksum):
        return str(self.account_id) + '/' + checksum

    def url(self, request):
        return request.relative_url(
            '/sandboxes/' + self._id)

    def upload(self, checksum, ifp):
        _id = str(self.account._id) + '/' + checksum
        chef_file.m.fs.delete(_id)
        with chef_file.m.fs.new_file(
            _id=_id,
            sandbox_id=self._id,
            needs_upload=False) as ofp:
            while True:
                chunk = ifp.read(self.CHUNKSIZE)
                if chunk: ofp.write(chunk)
                else: break
        if ofp.md5 != checksum:
            chef_file.m.fs.delete(_id)
            raise Invalid('Invalid checksum')

    def close(self):
        missing = [
            fobj._id.split('/')[-1]
            for fobj in chef_file.m.find(dict(
                sandbox_id=self._id, needs_upload=True)) ]
        if missing:
            raise Invalid(
                'Missing uploads',
                {}, None,
                error_dict=dict(
                   (k, 'Missing upload')
                   for k in missing))
        self.delete()

class ChefFile(ModelBase):
    pass

orm_session.mapper(Sandbox, sandbox, properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))
orm_session.mapper(ChefFile, chef_file,properties=dict(
        account_id=ForeignIdProperty('Account'),
        account=RelationProperty('Account')))

