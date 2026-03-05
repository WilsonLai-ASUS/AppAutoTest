"""Router httpd API client.

Implements username/password login via `login.cgi` to obtain `asus_token` and
provides a simple request helper that auto-logins when the token is missing.

Notes:
- Uses stdlib urllib (no third-party deps).
- Token is cached in-memory for the current Python process only.
"""

from __future__ import annotations

import base64
import json
import ssl
import time
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal

from .logger import logger


Scheme = Literal["http", "https"]
TokenTransport = Literal["query"]


class HttpResult:
    START = "START"
    OK = "OK"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    DNS_OK = "DNS_OK"
    DNS_FAIL = "DNS_FAIL"
    TCP_OK = "TCP_OK"
    TCP_FAIL = "TCP_FAIL"


def _mask_token(value: str) -> str:
    if not value:
        return value
    if len(value) <= 12:
        return "***"
    return f"{value[:6]}...{value[-4:]}"


def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    safe = dict(payload)
    if "asus_token" in safe and isinstance(safe["asus_token"], str):
        safe["asus_token"] = _mask_token(safe["asus_token"])
    return safe


def _sanitize_url(url: str) -> str:
    """Mask sensitive query params in URLs for logging."""
    try:
        parsed = urllib.parse.urlsplit(url)
        if not parsed.query:
            return url
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        sanitized: list[tuple[str, str]] = []
        for k, v in query:
            if k.lower() == "asus_token":
                sanitized.append((k, _mask_token(v)))
            else:
                sanitized.append((k, v))
        new_query = urllib.parse.urlencode(sanitized, doseq=True)
        return urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment)
        )
    except Exception:
        return url


def _exc_brief(e: Exception) -> str:
    if isinstance(e, urllib.error.URLError):
        reason = getattr(e, "reason", None)
        if isinstance(reason, Exception):
            return f"{type(e).__name__}(reason={type(reason).__name__}: {reason})"
        return f"{type(e).__name__}(reason={reason})"
    return f"{type(e).__name__}: {e}"


class HttpdApiError(Exception):
    pass


class HttpdLoginError(HttpdApiError):
    def __init__(self, message: str, *, error_status: int | None = None):
        super().__init__(message)
        self.error_status = error_status


class HttpdNotConfiguredError(HttpdApiError):
    pass


@dataclass(frozen=True)
class HttpdApiConfig:
    host: str
    scheme: Scheme = "http"
    port: int | None = None
    username: str | None = None
    password: str | None = None
    timeout_s: float = 10.0
    verify_tls: bool = True

    # Minimal/default token transport; can be extended later when you confirm
    # whether endpoints require cookie/header/query.
    token_transport: TokenTransport = "query"


class HttpdApi:
    """A minimal client for ASUS router httpd endpoints."""

    def __init__(self, config: HttpdApiConfig | None = None):
        self._config: HttpdApiConfig | None = config
        self._asus_token: str | None = None
        self._token_cache: dict[tuple[str, Scheme, int | None, str | None], str] = {}

    # ---------------------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------------------

    def configure(
        self,
        *,
        host: str,
        scheme: Scheme = "http",
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout_s: float = 10.0,
        verify_tls: bool = True,
    ) -> None:
        self._config = HttpdApiConfig(
            host=host,
            scheme=scheme,
            port=port,
            username=username,
            password=password,
            timeout_s=timeout_s,
            verify_tls=verify_tls,
        )

    # ---------------------------------------------------------------------
    # Token helpers
    # ---------------------------------------------------------------------

    def clear_token(self) -> None:
        self._asus_token = None
        if self._config is not None:
            key = (
                self._config.host,
                self._config.scheme,
                self._effective_port(self._config),
                self._config.username,
            )
            self._token_cache.pop(key, None)

    def asus_token(self) -> str | None:
        return self._asus_token

    def is_logged_in(self) -> bool:
        return bool(self._asus_token)

    def ensure_login(self) -> str:
        cfg = self._require_config()
        key = (cfg.host, cfg.scheme, self._effective_port(cfg), cfg.username)

        cached = self._token_cache.get(key)
        if cached:
            self._asus_token = cached
            return cached

        if self._asus_token:
            # Keep cache in sync if token was set directly.
            self._token_cache[key] = self._asus_token
            return self._asus_token
        return self.login()

    # ---------------------------------------------------------------------
    # HTTP helpers
    # ---------------------------------------------------------------------

    def _require_config(self) -> HttpdApiConfig:
        if self._config is None:
            raise HttpdNotConfiguredError("HttpdApi is not configured")
        if not self._config.host:
            raise HttpdNotConfiguredError("DUT host/ip is required")
        return self._config

    def _base_url(self) -> str:
        cfg = self._require_config()
        port = self._effective_port(cfg)
        return f"{cfg.scheme}://{cfg.host}:{port}"

    @staticmethod
    def _effective_port(cfg: HttpdApiConfig) -> int:
        if cfg.port is not None:
            return int(cfg.port)
        return 8443 if cfg.scheme == "https" else 80

    def _ssl_context(self) -> ssl.SSLContext | None:
        cfg = self._require_config()
        if cfg.scheme != "https":
            return None
        if cfg.verify_tls:
            return ssl.create_default_context()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_login: bool = False,
    ) -> tuple[int, dict[str, str], bytes]:
        cfg = self._require_config()

        if require_login:
            self.ensure_login()

        url = urllib.parse.urljoin(self._base_url() + "/", path.lstrip("/"))

        query: dict[str, Any] = {}
        if params:
            query.update(params)

        if require_login and cfg.token_transport == "query" and self._asus_token:
            query.setdefault("asus_token", self._asus_token)

        if query:
            url = (
                url
                + ("&" if urllib.parse.urlparse(url).query else "?")
                + urllib.parse.urlencode(query, doseq=True)
            )

        body: bytes | None = None
        req_headers = {"User-Agent": "AppAutoTest/HttpdApi"}
        if headers:
            req_headers.update(headers)

        if data is not None:
            body = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
            req_headers.setdefault(
                "Content-Type", "application/x-www-form-urlencoded; charset=utf-8"
            )

        req = urllib.request.Request(url=url, data=body, method=method.upper())
        for k, v in req_headers.items():
            req.add_header(k, v)

        started = time.monotonic()

        try:
            with urllib.request.urlopen(
                req, timeout=cfg.timeout_s, context=self._ssl_context()
            ) as resp:
                status = int(getattr(resp, "status", 200))
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                content = resp.read() or b""
                return status, resp_headers, content
        except urllib.error.HTTPError as e:
            # HTTPError is also a file-like response.
            status = int(getattr(e, "code", 0) or 0)
            resp_headers = (
                {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
            )
            content = e.read() if hasattr(e, "read") else b""
            return status, resp_headers, content
        except urllib.error.URLError as e:
            elapsed = time.monotonic() - started
            logger.error(
                "HttpdApi request url-error: %s %s (timeout=%.1fs verify_tls=%s, %.3f sec) %s",
                method.upper(),
                _sanitize_url(url),
                cfg.timeout_s,
                cfg.verify_tls,
                elapsed,
                _exc_brief(e),
            )
            raise

    def request_json(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        require_login: bool = True,
    ) -> dict[str, Any]:
        status, _, content = self._request(
            method=method,
            path=path,
            params=params,
            data=data,
            headers=headers,
            require_login=require_login,
        )

        if not content:
            raise HttpdApiError(f"Empty response body (HTTP {status})")

        try:
            payload = json.loads(content.decode("utf-8", errors="replace"))
        except Exception as e:
            raise HttpdApiError(f"Invalid JSON response (HTTP {status}): {e}") from e

        if not isinstance(payload, dict):
            raise HttpdApiError(f"JSON response is not an object (HTTP {status})")

        return payload

    # ---------------------------------------------------------------------
    # Login
    # ---------------------------------------------------------------------

    def login(self, username: str | None = None, password: str | None = None) -> str:
        cfg = self._require_config()

        user = username if username is not None else cfg.username
        pwd = password if password is not None else cfg.password

        if not user or not pwd:
            raise HttpdNotConfiguredError("username/password is required for login")

        api_name = "DUT_RT_GetAsusToken"
        login_url = urllib.parse.urljoin(self._base_url() + "/", "login.cgi")

        logger.info(
            "%s, %s, local, result : %s, 0.000 sec, scheme=%s host=%s port=%s timeout=%.1fs verify_tls=%s",
            api_name,
            login_url,
            HttpResult.START,
            cfg.scheme,
            cfg.host,
            self._effective_port(cfg),
            cfg.timeout_s,
            cfg.verify_tls,
        )

        # Quick connectivity probe to make timeouts actionable.
        probe_port = self._effective_port(cfg)
        probe_timeout_s = min(2.0, float(cfg.timeout_s or 10.0))

        try:
            addrinfos = socket.getaddrinfo(cfg.host, probe_port)
        except Exception as e:
            logger.error(
                "%s, %s, local, result : %s, 0.000 sec, reason=%s",
                api_name,
                login_url,
                HttpResult.DNS_FAIL,
                e,
            )
        else:
            resolved = []
            for family, _, _, _, sockaddr in addrinfos:
                ip = sockaddr[0] if isinstance(sockaddr, tuple) and sockaddr else None
                if ip:
                    resolved.append(f"{ip}({family})")
            if resolved:
                logger.info(
                    "%s, %s, local, result : %s, 0.000 sec, resolved=%s",
                    api_name,
                    login_url,
                    HttpResult.DNS_OK,
                    ",".join(sorted(set(resolved))),
                )

            started_probe = time.monotonic()
            try:
                with socket.create_connection(
                    (cfg.host, int(probe_port)), timeout=probe_timeout_s
                ) as sock:
                    elapsed_probe = time.monotonic() - started_probe
                    local_addr = None
                    try:
                        local_addr = sock.getsockname()
                    except Exception:
                        local_addr = None
                    logger.info(
                        "%s, %s, local, result : %s, %.3f sec, local_addr=%s",
                        api_name,
                        login_url,
                        HttpResult.TCP_OK,
                        elapsed_probe,
                        local_addr,
                    )
            except Exception as e:
                elapsed_probe = time.monotonic() - started_probe
                logger.error(
                    "%s, %s, local, result : %s, %.3f sec, reason=%s",
                    api_name,
                    login_url,
                    HttpResult.TCP_FAIL,
                    elapsed_probe,
                    e,
                )

        auth_raw = f"{user}:{pwd}".encode("utf-8")
        auth_b64 = base64.b64encode(auth_raw).decode("ascii")
        started = time.monotonic()
        try:
            # Matches your C flow: login_authorization=<base64(username:password)>
            payload = self.request_json(
                method="POST",
                path="login.cgi",
                data={"login_authorization": auth_b64},
                require_login=False,
            )
        except Exception as e:
            elapsed = time.monotonic() - started

            # Classify common network failures for readability.
            result = HttpResult.FAIL
            if isinstance(e, urllib.error.URLError) and isinstance(
                getattr(e, "reason", None), socket.timeout
            ):
                result = HttpResult.TIMEOUT

            logger.error(
                "%s, %s, local, result : %s, %.3f sec,",
                api_name,
                login_url,
                result,
                elapsed,
            )

            if isinstance(e, urllib.error.URLError):
                raise HttpdApiError(
                    f"{api_name}, {login_url}, local, result : {result}, {elapsed:.3f} sec, reason={e}"
                ) from e
            raise

        elapsed = time.monotonic() - started

        token = payload.get("asus_token")
        if isinstance(token, str) and token:
            self._asus_token = token
            key = (cfg.host, cfg.scheme, self._effective_port(cfg), cfg.username)
            self._token_cache[key] = token
            logger.info(
                "%s, %s, local, result : %s, %.3f sec,",
                api_name,
                login_url,
                HttpResult.OK,
                elapsed,
            )
            logger.info("[json]\n%s", json.dumps(_sanitize_payload(payload), indent=2))
            return token

        error_status = payload.get("error_status")
        err_int: int | None = None
        if isinstance(error_status, int):
            err_int = error_status
        elif isinstance(error_status, str) and error_status.isdigit():
            err_int = int(error_status)

        logger.error(
            "%s, %s, local, result : %s, %.3f sec,",
            api_name,
            login_url,
            HttpResult.FAIL,
            elapsed,
        )
        logger.error("[json]\n%s", json.dumps(_sanitize_payload(payload), indent=2))

        raise HttpdLoginError(f"Httpd login failed", error_status=err_int)


# Singleton (matches repo style)
httpd_api = HttpdApi()
