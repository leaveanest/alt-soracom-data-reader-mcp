"""tools/harvest.pyのテスト"""

from typing import Any
from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError
from soracom_data_mcp.tools.harvest import register_harvest_tools


class TestHarvestDataTools:
    """Harvest Dataツールのテスト"""

    @pytest.fixture
    def mcp_with_tools(self) -> FastMCP:
        """ツール登録済みのMCPインスタンス"""
        mcp = FastMCP("test-harvest")
        with patch("soracom_data_mcp.tools.harvest.soracom_client"):
            register_harvest_tools(mcp)
        return mcp

    def test_get_harvest_data_success(
        self, sample_harvest_data_response: list[dict[str, Any]]
    ) -> None:
        """get_harvest_data成功ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_harvest_data_response
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            # ツールを取得して実行
            tool = mcp._tool_manager._tools["get_harvest_data"]
            result = tool.fn(imsi="440103012345678")

            assert "data" in result
            assert result["count"] == 1
            mock_client.get.assert_called_once()

    def test_get_harvest_data_with_params(self) -> None:
        """get_harvest_dataパラメータ付きケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_data"]
            tool.fn(
                imsi="440103012345678",
                from_time=1609459200000,
                to_time=1609545600000,
                sort="asc",
                limit=50,
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["sort"] == "asc"
            assert params["limit"] == 50
            assert params["from"] == 1609459200000
            assert params["to"] == 1609545600000

    def test_get_harvest_data_limit_capped(self) -> None:
        """get_harvest_dataの上限確認"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_data"]
            tool.fn(imsi="440103012345678", limit=9999)

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["limit"] == 1000  # 上限でキャップされる

    def test_get_harvest_data_error(self) -> None:
        """get_harvest_dataエラーケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.side_effect = SoracomApiError("Not found", 404)
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_data"]
            result = tool.fn(imsi="invalid")

            assert "error" in result
            assert "404" in result["error"]

    def test_get_harvest_data_by_resource_success(self) -> None:
        """get_harvest_data_by_resource成功ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = [{"content": "test"}]
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_data_by_resource"]
            result = tool.fn(resource_type="device", resource_id="dev-123")

            assert "data" in result
            assert result["count"] == 1
            mock_client.get.assert_called_with(
                "/data/resources/device/dev-123",
                params={"sort": "desc", "limit": 100},
            )


class TestHarvestFilesTools:
    """Harvest Filesツールのテスト"""

    def test_list_harvest_files_success(self) -> None:
        """list_harvest_files成功ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = [
                {"filename": "test.json", "type": "file"}
            ]
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["list_harvest_files"]
            result = tool.fn()

            assert "files" in result
            assert result["count"] == 1

    def test_list_harvest_files_with_path(self) -> None:
        """list_harvest_filesパス指定ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["list_harvest_files"]
            tool.fn(scope="private", path="/subdir")

            # 先頭の/が除去されることを確認
            mock_client.get.assert_called_with(
                "/files/private/subdir", params={"limit": 100}
            )

    def test_list_harvest_files_root_path(self) -> None:
        """list_harvest_filesルートパスケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["list_harvest_files"]
            tool.fn(scope="private", path="/")

            mock_client.get.assert_called_with(
                "/files/private", params={"limit": 100}
            )

    def test_get_harvest_file_info_success(self) -> None:
        """get_harvest_file_info成功ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "totalSize": 1024,
                "fileCount": 10,
            }
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_file_info"]
            result = tool.fn()

            assert result["totalSize"] == 1024
            assert result["fileCount"] == 10

    def test_get_harvest_file_download_url_success(self) -> None:
        """get_harvest_file_download_url成功ケース"""
        with patch(
            "soracom_data_mcp.tools.harvest.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "url": "https://download.example.com/file"
            }
            mcp = FastMCP("test")
            register_harvest_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_file_download_url"]
            result = tool.fn(scope="private", path="/test.json")

            assert "url" in result
            mock_client.get.assert_called_with(
                "/files/private/test.json", params={"redirect": "false"}
            )

