"""config.pyのテスト"""

from unittest.mock import patch

import pytest

from soracom_data_mcp.config import Settings


class TestSettings:
    """Settingsクラスのテスト"""

    def test_default_values(self) -> None:
        """デフォルト値が正しく設定されることを確認"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            assert settings.soracom_auth_key_id is None
            assert settings.soracom_auth_key is None
            assert settings.soracom_coverage == "jp"

    def test_env_variables_loaded(self) -> None:
        """環境変数が正しく読み込まれることを確認"""
        env = {
            "SORACOM_AUTH_KEY_ID": "keyId-test123",
            "SORACOM_AUTH_KEY": "secret-test456",
            "SORACOM_COVERAGE": "g",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = Settings()
            assert settings.soracom_auth_key_id == "keyId-test123"
            assert settings.soracom_auth_key == "secret-test456"
            assert settings.soracom_coverage == "g"


class TestApiEndpoint:
    """api_endpointプロパティのテスト"""

    def test_japan_endpoint(self) -> None:
        """日本カバレッジのエンドポイントを確認"""
        with patch.dict("os.environ", {"SORACOM_COVERAGE": "jp"}, clear=True):
            settings = Settings()
            assert settings.api_endpoint == "https://api.soracom.io/v1"

    def test_global_endpoint(self) -> None:
        """グローバルカバレッジのエンドポイントを確認"""
        with patch.dict("os.environ", {"SORACOM_COVERAGE": "g"}, clear=True):
            settings = Settings()
            assert settings.api_endpoint == "https://g.api.soracom.io/v1"

    def test_default_is_japan(self) -> None:
        """デフォルトが日本カバレッジであることを確認"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            assert settings.api_endpoint == "https://api.soracom.io/v1"

    @pytest.mark.parametrize(
        "coverage,expected",
        [
            ("jp", "https://api.soracom.io/v1"),
            ("g", "https://g.api.soracom.io/v1"),
            ("unknown", "https://api.soracom.io/v1"),  # 未知の値はjpとして扱う
        ],
    )
    def test_endpoint_parametrized(self, coverage: str, expected: str) -> None:
        """パラメータ化テストでエンドポイントを確認"""
        with patch.dict("os.environ", {"SORACOM_COVERAGE": coverage}, clear=True):
            settings = Settings()
            assert settings.api_endpoint == expected

