import os
import traceback
from io import BytesIO

import requests
from django.conf import settings


class CloudStorageApiException(Exception):
    def __init__(self, message, status_code=None, text=None):
        super().__init__(message)
        self.status_code = status_code
        self.text = text


class UploadFailedException(CloudStorageApiException):
    ...


class EditFailedException(CloudStorageApiException):
    ...


class ExistsCheckFailedException(CloudStorageApiException):
    ...


class FileDoesNotExistException(CloudStorageApiException):
    ...


class DeleteFailedException(CloudStorageApiException):
    ...


class SizeCheckFailedException(CloudStorageApiException):
    ...


class ReadFailedException(CloudStorageApiException):
    ...


def get_setting_value(key: str, default=None):
    if hasattr(settings, key):
        return getattr(settings, key)

    return default


class CloudStorageApi:
    def __init__(self, url: str = None, api_token: str = None, project_alias: str = None):
        self.storage_url = url or get_setting_value('CLOUD_STORAGE_URL', '')
        self.api_token = api_token or get_setting_value('CLOUD_STORAGE_API_TOKEN', '')
        self.project_alias = project_alias or get_setting_value('CLOUD_STORAGE_PROJECT_ALIAS', '')

    @property
    def headers(self):
        return {'Api-Token': self.api_token}

    def upload(self, filename: str, content: bytes) -> dict:
        try:
            files = {'file': (filename, BytesIO(content))}
            response = requests.post(f'{self.storage_url}/api/upload', headers=self.headers, files=files)
        except Exception:
            raise UploadFailedException(traceback.format_exc())

        if not response.ok:
            raise UploadFailedException(
                f'Failed to upload the file {filename}.',
                response.status_code,
                response.text
            )

        return response.json()

    def edit(self, filename: str, content: bytes) -> dict:
        try:
            response = requests.post(
                f'{self.storage_url}/api/edit/{filename}',
                headers=self.headers,
                files={'file': (filename, BytesIO(content))}
            )
        except Exception:
            raise EditFailedException(traceback.format_exc())

        if not response.ok:
            raise EditFailedException(
                f'Failed to edit the file {filename}.',
                response.status_code,
                response.text
            )

        return response.json()

    def exists(self, filename: str) -> bool:
        try:
            response = requests.get(f'{self.storage_url}/api/exists/{filename}', headers=self.headers)
        except Exception:
            raise ExistsCheckFailedException(traceback.format_exc())

        if response.ok:
            return response.json()['exists']

        if response.status_code == 404:
            raise FileDoesNotExistException(f'File {filename} does not exist.')

        raise ExistsCheckFailedException(
            f'Check for existence failed for the file {filename}.',
            response.status_code,
            response.text
        )

    def delete(self, filename: str) -> bool:
        try:
            response = requests.delete(f'{self.storage_url}/api/delete/{filename}', headers=self.headers)
        except Exception:
            raise DeleteFailedException(traceback.format_exc())

        if response.status_code == 200:
            return response.json()['delete']

        if response.status_code == 404:
            raise DeleteFailedException('File does not exist.')

        raise DeleteFailedException(
            f'Delete operation failed for the file {filename}.',
            response.status_code,
            response.text
        )

    def size(self, filename: str) -> int:
        try:
            response = requests.get(f'{self.storage_url}/size/{filename}', headers=self.headers)
        except Exception:
            raise SizeCheckFailedException(traceback.format_exc())

        if response.status_code == 200:
            return response.json()['size']

        if response.status_code == 404:
            raise SizeCheckFailedException('File does not exist.')

        raise SizeCheckFailedException(
            f'Check for size failed for the file {filename}.',
            response.status_code,
            response.text
        )

    def url(self, filename: str, width: int = None, height: int = None) -> str:
        if width and height:
            name, extension = os.path.splitext(filename)

            return f'{self.storage_url}/{self.project_alias}/{name}_{width}x{height}{extension}'

        return f'{self.storage_url}/{self.project_alias}/{filename}'

    def read(self, filename: str) -> bytes:
        try:
            response = requests.get(self.url(filename))
        except Exception:
            raise ReadFailedException(traceback.format_exc())

        if not response.ok:
            raise ReadFailedException(
                f'Read operation failed for the file {filename}',
                response.status_code,
                response.text
            )

        return response.content
