"""設定管理 - 環境変数から認証情報等を読み込み"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """SORACOM MCP設定"""

    # SORACOM 認証キー
    soracom_auth_key_id: str | None = None  # keyId-xxx
    soracom_auth_key: str | None = None  # secret-xxx

    # カバレッジタイプ（jp: 日本, g: グローバル）
    soracom_coverage: str = "jp"

    model_config = {
        "env_prefix": "",  # 環境変数のプレフィックスなし
        "case_sensitive": False,
    }

    @property
    def api_endpoint(self) -> str:
        """カバレッジに応じたAPIエンドポイントを返す"""
        if self.soracom_coverage == "g":
            return "https://g.api.soracom.io/v1"
        return "https://api.soracom.io/v1"


# シングルトンインスタンス
settings = Settings()

