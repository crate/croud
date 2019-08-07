import requests
import uuid
from argparse import Namespace
from functools import partial

from aiohttp import ContentTypeError  # type: ignore

from croud.config import Configuration
from croud.session import HttpSession, RequestMethod


class Client:
    _env: str
    _token: str
    _region: str
    _sudo: bool

    def __init__(self, env: str, region: str, sudo: bool = False):
        self._env = env or Configuration.get_env()
        self._token = Configuration.get_token(self._env)
        self._region = region or Configuration.get_setting("region")
        self._sudo = sudo

    @staticmethod
    def from_args(args: Namespace) -> "Client":
        return Client(env=args.env, region=args.region, sudo=args.sudo)

    def send(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        body: dict = None,
        params: dict = None
    ):
        return self.fetch(method, endpoint, body, params)

    def fetch(
        self,
        method: RequestMethod,
        endpoint: str,
        body: dict = None,
        params: dict = None,
    ):
        with HttpSession(
            self._env,
            self._token,
            self._region,
            on_new_token=partial(Configuration.set_token, env=self._env),
            headers={"X-Auth-Sudo": str(uuid.uuid4())} if self._sudo is True else {},
        ) as session:
            resp = session.fetch(method, endpoint, body, params)
            return self._decode_response(resp)

    def _decode_response(self, resp: requests.Response):
        if resp.status_code == 204:
            # response is empty
            return None, None

        try:
            body = resp.json()
        # API always returns JSON, unless there's an unhandled server error
        except ContentTypeError:
            body = {"message": "Invalid response type.", "success": False}

        if resp.status_code >= 400:
            return None, body
        else:
            return body, None
