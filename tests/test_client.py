"""client.pyのテスト"""

import time
from unittest.mock import MagicMock, patch

import pytest

from soracom_data_mcp.client import (
    SoracomApiError,
    SoracomClient,
    handle_soracom_error,
)


class TestSoracomApiError:
    """SoracomApiErrorクラスのテスト"""

    def test_error_with_status_code(self) -> None:
        """ステータスコード付きエラーを確認"""
        error = SoracomApiError("テストエラー", status_code=404)
        assert error.message == "テストエラー"
        assert error.status_code == 404
        assert str(error) == "テストエラー"

    def test_error_without_status_code(self) -> None:
        """ステータスコードなしエラーを確認"""
        error = SoracomApiError("テストエラー")
        assert error.message == "テストエラー"
        assert error.status_code is None


class TestHandleSoracomError:
    """handle_soracom_error関数のテスト"""

    def test_format_with_status_code(self) -> None:
        """ステータスコード付きフォーマットを確認"""
        error = SoracomApiError("APIエラー: 認証失敗", status_code=401)
        result = handle_soracom_error(error)
        assert result == "SORACOM APIエラー (401): APIエラー: 認証失敗"

    def test_format_without_status_code(self) -> None:
        """ステータスコードなしフォーマットを確認"""
        error = SoracomApiError("ネットワークエラー")
        result = handle_soracom_error(error)
        assert result == "SORACOM APIエラー: ネットワークエラー"


class TestSoracomClient:
    """SoracomClientクラスのテスト"""

    def test_client_initialization(self) -> None:
        """クライアント初期化を確認"""
        client = SoracomClient()
        assert client._api_key is None
        assert client._token is None
        assert client._token_expires_at == 0
        assert client._client is None

    def test_lazy_client_initialization(self) -> None:
        """遅延初期化を確認"""
        client = SoracomClient()
        assert client._client is None
        # clientプロパティアクセスでhttpx.Clientが作成される
        with patch("httpx.Client") as mock_httpx:
            mock_httpx.return_value = MagicMock()
            _ = client.client
            mock_httpx.assert_called_once_with(timeout=30.0)

    def test_authentication_required_error(self) -> None:
        """認証情報なしでエラーになることを確認"""
        client = SoracomClient()
        with (
            patch.dict(
                "os.environ",
                {"SORACOM_AUTH_KEY_ID": "", "SORACOM_AUTH_KEY": ""},
                clear=True,
            ),
            patch("soracom_data_mcp.config.settings") as mock_settings,
        ):
            mock_settings.soracom_auth_key_id = None
            mock_settings.soracom_auth_key = None
            with pytest.raises(SoracomApiError) as exc_info:
                client._authenticate()
            assert "SORACOM_AUTH_KEY_ID と SORACOM_AUTH_KEY を設定してください" in str(
                exc_info.value
            )

    def test_authenticate_success(self) -> None:
        """認証成功を確認"""
        client = SoracomClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "apiKey": "test-api-key",
            "token": "test-token",
            "tokenTimeoutSeconds": 3600,
        }

        mock_http_client = MagicMock()
        mock_http_client.post.return_value = mock_response
        client._client = mock_http_client

        with patch("soracom_data_mcp.client.settings") as mock_settings:
            mock_settings.soracom_auth_key_id = "keyId-test"
            mock_settings.soracom_auth_key = "secret-test"
            mock_settings.api_endpoint = "https://api.soracom.io/v1"

            client._authenticate()

            assert client._api_key == "test-api-key"
            assert client._token == "test-token"
            assert client._token_expires_at > time.time()

    def test_authenticate_failure(self) -> None:
        """認証失敗を確認"""
        client = SoracomClient()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid credentials"}

        mock_http_client = MagicMock()
        mock_http_client.post.return_value = mock_response
        client._client = mock_http_client

        with patch("soracom_data_mcp.client.settings") as mock_settings:
            mock_settings.soracom_auth_key_id = "keyId-test"
            mock_settings.soracom_auth_key = "secret-test"
            mock_settings.api_endpoint = "https://api.soracom.io/v1"

            with pytest.raises(SoracomApiError) as exc_info:
                client._authenticate()

            assert exc_info.value.status_code == 401

    def test_ensure_authenticated_reuses_valid_token(self) -> None:
        """有効なトークンが再利用されることを確認"""
        client = SoracomClient()
        client._token = "existing-token"
        client._token_expires_at = time.time() + 600  # 10分後

        with patch.object(client, "_authenticate") as mock_auth:
            client._ensure_authenticated()
            mock_auth.assert_not_called()

    def test_ensure_authenticated_refreshes_expired_token(self) -> None:
        """期限切れトークンが更新されることを確認"""
        client = SoracomClient()
        client._token = "expired-token"
        client._token_expires_at = time.time() - 100  # 過去

        with patch.object(client, "_authenticate") as mock_auth:
            client._ensure_authenticated()
            mock_auth.assert_called_once()

    def test_get_headers(self) -> None:
        """ヘッダー取得を確認"""
        client = SoracomClient()
        client._api_key = "test-api-key"
        client._token = "test-token"
        client._token_expires_at = time.time() + 600

        headers = client._get_headers()

        assert headers["X-Soracom-API-Key"] == "test-api-key"
        assert headers["X-Soracom-Token"] == "test-token"
        assert headers["Content-Type"] == "application/json"

    def test_request_success(self) -> None:
        """リクエスト成功を確認"""
        client = SoracomClient()
        client._api_key = "test-api-key"
        client._token = "test-token"
        client._token_expires_at = time.time() + 600

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_http_client = MagicMock()
        mock_http_client.request.return_value = mock_response
        client._client = mock_http_client

        with patch("soracom_data_mcp.config.settings") as mock_settings:
            mock_settings.api_endpoint = "https://api.soracom.io/v1"
            result = client.request("GET", "/test")

        assert result == {"data": "test"}

    def test_request_404_error(self) -> None:
        """404エラーを確認"""
        client = SoracomClient()
        client._api_key = "test-api-key"
        client._token = "test-token"
        client._token_expires_at = time.time() + 600

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}

        mock_http_client = MagicMock()
        mock_http_client.request.return_value = mock_response
        client._client = mock_http_client

        with (
            patch("soracom_data_mcp.config.settings") as mock_settings,
            pytest.raises(SoracomApiError) as exc_info,
        ):
            mock_settings.api_endpoint = "https://api.soracom.io/v1"
            client.request("GET", "/test")

        assert exc_info.value.status_code == 404

    def test_request_204_no_content(self) -> None:
        """204 No Contentレスポンスを確認"""
        client = SoracomClient()
        client._api_key = "test-api-key"
        client._token = "test-token"
        client._token_expires_at = time.time() + 600

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_http_client = MagicMock()
        mock_http_client.request.return_value = mock_response
        client._client = mock_http_client

        with patch("soracom_data_mcp.config.settings") as mock_settings:
            mock_settings.api_endpoint = "https://api.soracom.io/v1"
            result = client.request("DELETE", "/test")

        assert result == {}

    def test_get_method(self) -> None:
        """GETメソッドを確認"""
        client = SoracomClient()
        with patch.object(client, "request") as mock_request:
            mock_request.return_value = {"data": "test"}
            result = client.get("/test", params={"key": "value"})
            mock_request.assert_called_once_with(
                "GET", "/test", params={"key": "value"}
            )
            assert result == {"data": "test"}

    def test_post_method(self) -> None:
        """POSTメソッドを確認"""
        client = SoracomClient()
        with patch.object(client, "request") as mock_request:
            mock_request.return_value = {"data": "test"}
            result = client.post("/test", json={"body": "data"})
            mock_request.assert_called_once_with(
                "POST", "/test", params=None, json={"body": "data"}
            )
            assert result == {"data": "test"}

