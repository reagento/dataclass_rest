import urllib.parse
from json import JSONDecodeError
from typing import Any, Optional, Tuple

from httpx import AsyncClient, Response, HTTPError, Client

from dataclass_rest.base_client import BaseClient
from dataclass_rest.boundmethod import AsyncMethod, SyncMethod
from dataclass_rest.exceptions import (
    ClientError,
    ClientLibraryError,
    MalformedResponse,
    ServerError,
)
from dataclass_rest.http_request import HttpRequest, File


class AsyncHttpxMethod(AsyncMethod):
    def _on_error_default(self, response: Response) -> Any:
        if 400 <= response.status_code < 500:
            raise ClientError(response.status_code)
        else:
            raise ServerError(response.status_code)

    async def _release_raw_response(self, response: Response) -> None:
        await response.aclose()

    async def _response_body(self, response: Response) -> Any:
        try:
            return response.json()
        except HTTPError as e:
            raise ClientLibraryError from e
        except JSONDecodeError as e:
            raise MalformedResponse from e

    async def _response_ok(self, response: Response) -> bool:
        return response.is_success


class AsyncHttpxClient(BaseClient):
    method_class = AsyncHttpxMethod

    def __init__(
            self,
            base_url: str,
            client: Optional[AsyncClient] = None,
    ):
        super().__init__()
        self.client = client or AsyncClient()
        self.base_url = base_url

    def _prepare_file(self, fieldname: str, file: File) -> Tuple:
        return (file.filename or fieldname, file.contents, file.content_type)

    async def do_request(self, request: HttpRequest) -> Any:
        if request.is_json_request:
            json = request.data
            data = None
        else:
            json = None
            data = request.data

        files = {
            name: self._prepare_file(name, file)
            for name, file in request.files.items()
        }
        try:
            return await self.client.request(
                url=urllib.parse.urljoin(self.base_url, request.url),
                method=request.method,
                json=json,
                params=request.query_params,
                data=data,
                headers=request.headers,
                files=files,
            )
        except HTTPError as e:
            raise ClientLibraryError from e


class HttpxMethod(SyncMethod):
    def _on_error_default(self, response: Response) -> Any:
        if 400 <= response.status_code < 500:
            raise ClientError(response.status_code)
        else:
            raise ServerError(response.status_code)

    def _release_raw_response(self, response: Response) -> None:
        response.aclose()

    def _response_body(self, response: Response) -> Any:
        try:
            return response.json()
        except HTTPError as e:
            raise ClientLibraryError from e
        except JSONDecodeError as e:
            raise MalformedResponse from e

    def _response_ok(self, response: Response) -> bool:
        return response.is_success


class HttpxClient(BaseClient):
    method_class = HttpxMethod

    def __init__(
            self,
            base_url: str,
            client: Optional[Client] = None,
    ):
        super().__init__()
        self.client = client or Client()
        self.base_url = base_url

    def _prepare_file(self, fieldname: str, file: File) -> Tuple:
        return (file.filename or fieldname, file.contents, file.content_type)

    def do_request(self, request: HttpRequest) -> Any:
        if request.is_json_request:
            json = request.data
            data = None
        else:
            json = None
            data = request.data

        files = {
            name: self._prepare_file(name, file)
            for name, file in request.files.items()
        }
        try:
            return self.client.request(
                url=urllib.parse.urljoin(self.base_url, request.url),
                method=request.method,
                json=json,
                params=request.query_params,
                data=data,
                headers=request.headers,
                files=files,
            )
        except HTTPError as e:
            raise ClientLibraryError from e
