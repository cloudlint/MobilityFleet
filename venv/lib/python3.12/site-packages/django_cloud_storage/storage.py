from io import BytesIO

from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.utils import validate_file_name
from django_cloud_storage.api import CloudStorageApi, ReadFailedException, ExistsCheckFailedException, \
    UploadFailedException, \
    DeleteFailedException, SizeCheckFailedException, EditFailedException, FileDoesNotExistException


class CloudStorageException(Exception):
    ...


class CloudFile(File):
    def __init__(self, name, storage, mode, edit=False):
        self.name = name
        self._storage = storage
        self._mode = mode
        self._size = None
        self.file = None
        self._is_dirty = False
        self._is_read = False
        self._edit = edit

    @property
    def size(self):
        if not self._size:
            if self._is_read:
                self._size = len(self.file)
            else:
                self._size = self._storage.size(self.name)

        return self._size

    def read(self, num_bytes=None):
        if 'r' not in self._mode:
            raise AttributeError('File was opened for write-only access.')

        if not self._is_read:
            self.file = self._storage._read(self.name)
            self._is_read = True
        return self.file.read(num_bytes)

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError('File was opened for read-only access.')

        self.file = BytesIO(content)
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            if self._edit:
                self._storage._edit(self.name, self.file)
            else:
                self._storage._save(self.name, self.file)
        self.file.close()


class CloudStorage(Storage):
    def __init__(self, api: CloudStorageApi = None):
        self._api = api or CloudStorageApi()

    def _open(self, name, mode='rb'):
        try:
            self._api.exists(name)
        except FileDoesNotExistException:
            raise FileNotFoundError(f'File does not exist: {name}')
        except ExistsCheckFailedException:
            raise CloudStorageException(f'Exists operation failed for the file: {name}')

        cloud_file = CloudFile(name, self, mode=mode, edit=True)

        return cloud_file

    def _read(self, name):

        try:
            return BytesIO(self._api.read(name))
        except ReadFailedException:
            raise CloudStorageException(f'Read operation failed for the file: {name}')

    def _save(self, name, content):
        try:
            f = self._api.upload(name, content.read())
            return f['name']
        except UploadFailedException:
            raise CloudStorageException(f'Save operation failed for the file: {name}')

    def _edit(self, name, content):
        try:
            f = self._api.edit(name, content)
            return f['name']
        except EditFailedException:
            raise CloudStorageException(f'Edit operation failed for the file: {name}')

    def delete(self, name):
        try:
            self._api.delete(name)
        except DeleteFailedException:
            raise CloudStorageException(f'Delete operation failed for the file: {name}')

    def size(self, name):
        try:
            return self._api.size(name)
        except SizeCheckFailedException:
            raise CloudStorageException(f'Size operation failed for the file: {name}')

    def exists(self, name):
        try:
            return self._api.exists(name)
        except FileDoesNotExistException:
            return False
        except ExistsCheckFailedException:
            raise CloudStorageException(f'Exists operation failed for the file: {name}')

    def url(self, name, width=None, height=None):
        return self._api.url(name, width, height)

    def save(self, name, content, max_length=None):
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self._save(name, content)

        validate_file_name(name, allow_relative_path=True)

        return name
