"""SORACOM APIクライアント"""

import time
from typing import Any

import httpx

from soracom_data_mcp.config import settings


class SoracomApiError(Exception):
    """SORACOM APIエラー"""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SoracomClient:
    """SORACOM APIクライアントラッパー"""

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._token: str | None = None
        self._token_expires_at: float = 0
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """HTTPクライアントを取得（遅延初期化）"""
        if self._client is None:
            self._client = httpx.Client(timeout=30.0)
        return self._client

    def _ensure_authenticated(self) -> None:
        """認証済みであることを確認し、必要なら認証を行う"""
        # トークンが有効期限切れ前（5分のマージン）かチェック
        if self._token and time.time() < self._token_expires_at - 300:
            return

        self._authenticate()

    def _authenticate(self) -> None:
        """SORACOM APIで認証してトークンを取得"""
        if not settings.soracom_auth_key_id or not settings.soracom_auth_key:
            raise SoracomApiError(
                "SORACOM_AUTH_KEY_ID と SORACOM_AUTH_KEY を設定してください"
            )

        response = self.client.post(
            f"{settings.api_endpoint}/auth",
            json={
                "authKeyId": settings.soracom_auth_key_id,
                "authKey": settings.soracom_auth_key,
            },
        )

        if response.status_code != 200:
            error_detail = response.json().get("message", response.text)
            raise SoracomApiError(
                f"認証に失敗しました: {error_detail}",
                status_code=response.status_code,
            )

        data = response.json()
        self._api_key = data.get("apiKey")
        self._token = data.get("token")

        # トークン有効期限（ミリ秒→秒に変換）
        token_timeout_seconds = data.get("tokenTimeoutSeconds", 86400)
        self._token_expires_at = time.time() + token_timeout_seconds

    def _get_headers(self) -> dict[str, str]:
        """認証ヘッダーを取得"""
        self._ensure_authenticated()
        return {
            "X-Soracom-API-Key": self._api_key or "",
            "X-Soracom-Token": self._token or "",
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """汎用APIリクエスト"""
        url = f"{settings.api_endpoint}{path}"
        headers = self._get_headers()

        response = self.client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("message", response.text)
            except Exception:
                error_message = response.text
            raise SoracomApiError(
                f"APIエラー: {error_message}",
                status_code=response.status_code,
            )

        if response.status_code == 204:
            return {}

        result: dict[str, Any] | list[Any] = response.json()
        return result

    def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[Any]:
        """GETリクエスト"""
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """POSTリクエスト"""
        return self.request("POST", path, params=params, json=json)


# シングルトンインスタンス
soracom_client = SoracomClient()


def handle_soracom_error(e: SoracomApiError) -> str:
    """SORACOM APIエラーをフォーマット"""
    if e.status_code:
        return f"SORACOM APIエラー ({e.status_code}): {e.message}"
    return f"SORACOM APIエラー: {e.message}"

