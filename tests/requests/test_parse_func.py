#from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import requests
import requests_mock

from dataclass_rest import get, post
from dataclass_rest.http.requests import RequestsClient


@dataclass
class TestBody:
    value: int


def test_string_hints(session: requests.Session, mocker: requests_mock.Mocker):
    class Api(RequestsClient):
        @get("/items/{item_id}")
        def get_item(self, item_id: "str") -> "List[int]":
            raise NotImplementedError

        @post("/items")
        def create_item(self, body: "TestBody") -> "Optional[int]":
            raise NotImplementedError

    mocker.get("http://example.com/items/1", text="[1, 2, 3]", complete_qs=True)
    mocker.post("http://example.com/items", text="1", complete_qs=True)

    client = Api(base_url="http://example.com", session=session)

    assert client.get_item("1") == [1, 2, 3]
    assert client.create_item(TestBody(value=5)) == 1
