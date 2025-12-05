"""tools/stats.pyのテスト"""

from typing import Any
from unittest.mock import patch

from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError
from soracom_data_mcp.tools.stats import register_stats_tools


class TestSubscriberTools:
    """SIM（Subscriber）ツールのテスト"""

    def test_list_subscribers_success(
        self, sample_subscriber_response: list[dict[str, Any]]
    ) -> None:
        """list_subscribers成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_subscriber_response
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_subscribers"]
            result = tool.fn()

            assert "subscribers" in result
            assert result["count"] == 1
            assert result["subscribers"][0]["imsi"] == "440103012345678"
            assert result["subscribers"][0]["status"] == "active"

    def test_list_subscribers_with_filters(self) -> None:
        """list_subscribersフィルタ付きケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_subscribers"]
            tool.fn(
                status_filter="active",
                speed_class_filter="s1.standard",
                tag_name="env",
                tag_value="production",
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["status_filter"] == "active"
            assert params["speed_class_filter"] == "s1.standard"
            assert params["tag_name"] == "env"
            assert params["tag_value"] == "production"

    def test_list_subscribers_limit_capped(self) -> None:
        """list_subscribersの上限確認"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_subscribers"]
            tool.fn(limit=500)

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["limit"] == 100  # 上限でキャップされる

    def test_list_subscribers_error(self) -> None:
        """list_subscribersエラーケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.side_effect = SoracomApiError("Unauthorized", 401)
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_subscribers"]
            result = tool.fn()

            assert "error" in result
            assert "401" in result["error"]

    def test_get_subscriber_success(self) -> None:
        """get_subscriber成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "imsi": "440103012345678",
                "msisdn": "818012345678",
                "iccid": "8981100000000000001",
                "status": "active",
                "speedClass": "s1.standard",
                "tags": {"name": "TestSIM"},
                "groupId": "group-12345",
                "subscription": "plan-D",
                "moduleType": "mini",
                "plan": 1,
                "createdAt": 1609459200000,
                "lastModifiedAt": 1609459200000,
                "sessionStatus": {},
            }
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_subscriber"]
            result = tool.fn(imsi="440103012345678")

            assert result["imsi"] == "440103012345678"
            assert result["status"] == "active"
            assert result["module_type"] == "mini"


class TestGroupTools:
    """グループツールのテスト"""

    def test_list_groups_success(
        self, sample_group_response: list[dict[str, Any]]
    ) -> None:
        """list_groups成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_group_response
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_groups"]
            result = tool.fn()

            assert "groups" in result
            assert result["count"] == 1
            assert result["groups"][0]["group_id"] == "group-12345"

    def test_list_groups_with_tags(self) -> None:
        """list_groupsタグフィルタケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["list_groups"]
            tool.fn(
                tag_name="project",
                tag_value="demo",
                tag_value_match_mode="prefix",
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["tag_name"] == "project"
            assert params["tag_value"] == "demo"
            assert params["tag_value_match_mode"] == "prefix"

    def test_get_group_success(self) -> None:
        """get_group成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "groupId": "group-12345",
                "tags": {"name": "TestGroup"},
                "configuration": {"harvest": {"enabled": True}},
                "createdAt": 1609459200000,
                "lastModifiedAt": 1609459200000,
            }
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_group"]
            result = tool.fn(group_id="group-12345")

            assert result["group_id"] == "group-12345"
            assert result["configuration"]["harvest"]["enabled"] is True


class TestStatsTools:
    """統計ツールのテスト"""

    def test_get_air_stats_success(
        self, sample_air_stats_response: list[dict[str, Any]]
    ) -> None:
        """get_air_stats成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_air_stats_response
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_air_stats"]
            result = tool.fn(
                imsi="440103012345678",
                from_time=1609459200,
                to_time=1609545600,
            )

            assert "stats" in result
            assert result["count"] == 1
            assert result["stats"][0]["upload_bytes"] == 1000
            assert result["stats"][0]["download_bytes"] == 2000
            assert result["imsi"] == "440103012345678"
            assert result["period"] == "day"

    def test_get_air_stats_with_period(self) -> None:
        """get_air_stats期間指定ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_air_stats"]
            tool.fn(
                imsi="440103012345678",
                from_time=1609459200,
                to_time=1609545600,
                period="month",
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["period"] == "month"

    def test_get_air_stats_error(self) -> None:
        """get_air_statsエラーケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.side_effect = SoracomApiError("Not found", 404)
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_air_stats"]
            result = tool.fn(
                imsi="invalid",
                from_time=1609459200,
                to_time=1609545600,
            )

            assert "error" in result
            assert "404" in result["error"]

    def test_get_harvest_stats_success(self) -> None:
        """get_harvest_stats成功ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = [
                {
                    "date": "2024-01-01",
                    "count": 100,
                    "bytes": 5000,
                }
            ]
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_stats"]
            result = tool.fn(
                imsi="440103012345678",
                from_time=1609459200,
                to_time=1609545600,
            )

            assert "stats" in result
            assert result["count"] == 1
            assert result["stats"][0]["count"] == 100
            assert result["stats"][0]["bytes"] == 5000

    def test_get_harvest_stats_with_month_period(self) -> None:
        """get_harvest_stats月次期間ケース"""
        with patch(
            "soracom_data_mcp.tools.stats.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_stats_tools(mcp)

            tool = mcp._tool_manager._tools["get_harvest_stats"]
            tool.fn(
                imsi="440103012345678",
                from_time=1609459200,
                to_time=1609545600,
                period="month",
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["period"] == "month"
            mock_client.get.assert_called_with(
                "/stats/harvest/subscribers/440103012345678",
                params={"from": 1609459200, "to": 1609545600, "period": "month"},
            )

