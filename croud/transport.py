import uuid
from argparse import Namespace
from enum import Enum
from typing import Callable
from requests import Response, Session
from requests.cookies import cookiejar_from_dict
from yarl import URL

from croud.config import Configuration
from croud.printer import print_error

CLOUD_LOCAL_URL = "http://localhost:8000"
CLOUD_DEV_DOMAIN = "cratedb-dev.cloud"
CLOUD_PROD_DOMAIN = "cratedb.cloud"


class RequestMethod(Enum):
    GET = "get"
    POST = "post"
    DELETE = "delete"
    PATCH = "patch"
    PUT = "put"


class Client:
    _env: str
    _token: str
    _region: str
    _sudo: bool
    _session: Session
    _on_new_token: Callable[[str], None] = None

    def __init__(self, env: str, region: str, sudo: bool = False):
        self._env = env or Configuration.get_env()
        self._token = Configuration.get_token(self._env)
        self._region = region or Configuration.get_setting("region")
        self._sudo = sudo
        self._session = Session()
        self._session.headers = (
            {"X-Auth-Sudo": str(uuid.uuid4())} if self._sudo is True else {}
        )
        self._session.cookies = cookiejar_from_dict({"session": self._token})

    @staticmethod
    def from_args(args: Namespace) -> "Client":
        return Client(env=args.env, region=args.region, sudo=args.sudo)

    def send(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        body: dict = None,
        params: dict = None,
    ):
        with self._session as session:
            prep_url = cloud_url(self._env, self._region)
            url = URL(prep_url).with_path(endpoint)
            resp = getattr(session, method.value)(
                url, json=body, allow_redirects=False, params=params
            )
            if resp.status_code == 302:  # login redirect
                print_error(
                    "Unauthorized. Use `croud login` to login to CrateDB Cloud."
                )
                exit(1)
            self.close()
            return self._decode_response(resp)

    def _decode_response(self, resp: Response):
        if resp.status_code == 204:
            # response is empty
            return None, None
        # try:
        body = resp.json()
        # API always returns JSON, unless there's an unhandled server error
        # except ContentTypeError:
        #     body = {"message": "Invalid response type.", "success": False}

        if resp.status_code >= 400:
            return None, body
        else:
            return body, None

    def close(self) -> None:
        new_token = self._session.cookies.get("session")
        if new_token and self._token != new_token and self._on_new_token:
            self._on_new_token(new_token)
        self._session.close()


def session_logout(session: Session, url: str):
    session.get(url)


def cloud_url(env: str, region: str = "bregenz.a1") -> str:
    if env == "local":
        return CLOUD_LOCAL_URL

    host = CLOUD_DEV_DOMAIN if env == "dev" else CLOUD_PROD_DOMAIN
    return f"https://{region}.{host}"
