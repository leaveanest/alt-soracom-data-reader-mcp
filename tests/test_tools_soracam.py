"""tools/soracam.pyのテスト"""

from typing import Any
from unittest.mock import patch

from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError
from soracom_data_mcp.tools.soracam import register_soracam_tools


class TestSoracamDeviceTools:
    """SoraCamデバイスツールのテスト"""

    def test_list_soracam_devices_success(
        self, sample_soracam_device_response: list[dict[str, Any]]
    ) -> None:
        """list_soracam_devices成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_soracam_device_response
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_devices"]
            result = tool.fn()

            assert "devices" in result
            assert result["count"] == 1
            assert result["devices"][0]["device_id"] == "ABC123DEF456"
            assert result["devices"][0]["name"] == "TestCamera"

    def test_list_soracam_devices_with_pagination(self) -> None:
        """list_soracam_devicesページネーションケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_devices"]
            tool.fn(limit=50, last_evaluated_key="key123")

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["limit"] == 50
            assert params["last_evaluated_key"] == "key123"

    def test_list_soracam_devices_error(self) -> None:
        """list_soracam_devicesエラーケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.side_effect = SoracomApiError("API Error", 500)
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_devices"]
            result = tool.fn()

            assert "error" in result
            assert "500" in result["error"]

    def test_get_soracam_device_success(self) -> None:
        """get_soracam_device成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "deviceId": "ABC123DEF456",
                "name": "TestCamera",
                "status": "active",
                "connected": True,
                "firmwareVersion": "1.0.0",
                "configuration": {"resolution": "1080p"},
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["get_soracam_device"]
            result = tool.fn(device_id="ABC123DEF456")

            assert result["device_id"] == "ABC123DEF456"
            assert result["name"] == "TestCamera"
            assert result["configuration"] == {"resolution": "1080p"}


class TestSoracamEventTools:
    """SoraCamイベントツールのテスト"""

    def test_list_soracam_events_success(
        self, sample_soracam_event_response: list[dict[str, Any]]
    ) -> None:
        """list_soracam_events成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = sample_soracam_event_response
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_events"]
            result = tool.fn(device_id="ABC123DEF456")

            assert "events" in result
            assert result["count"] == 1
            assert result["events"][0]["event_type"] == "atomCamPersonDetected"

    def test_list_soracam_events_with_time_range(self) -> None:
        """list_soracam_eventsタイム範囲指定ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = []
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_events"]
            tool.fn(
                device_id="ABC123DEF456",
                from_time=1609459200000,
                to_time=1609545600000,
                sort="asc",
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["from"] == 1609459200000
            assert params["to"] == 1609545600000
            assert params["sort"] == "asc"

    def test_get_soracam_event_success(self) -> None:
        """get_soracam_event成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "eventId": "event-12345",
                "deviceId": "ABC123DEF456",
                "eventType": "atomCamPersonDetected",
                "time": 1609459200000,
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["get_soracam_event"]
            result = tool.fn(device_id="ABC123DEF456", event_id="event-12345")

            assert result["event_id"] == "event-12345"
            assert result["event_type"] == "atomCamPersonDetected"


class TestSoracamRecordingTools:
    """SoraCam録画ツールのテスト"""

    def test_list_soracam_recordings_success(self) -> None:
        """list_soracam_recordings成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "recordings": [
                    {"from": 1609459200000, "to": 1609462800000}
                ],
                "events": [
                    {"eventId": "evt1", "eventType": "motion"}
                ],
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_recordings"]
            result = tool.fn(device_id="ABC123DEF456")

            assert "recordings" in result
            assert "events" in result
            assert len(result["recordings"]) == 1

    def test_list_soracam_recordings_with_time_range(self) -> None:
        """list_soracam_recordingsタイム範囲指定ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {"recordings": [], "events": []}
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["list_soracam_recordings"]
            tool.fn(
                device_id="ABC123DEF456",
                from_time=1609459200000,
                to_time=1609545600000,
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["from"] == 1609459200000
            assert params["to"] == 1609545600000

    def test_export_soracam_image_success(self) -> None:
        """export_soracam_image成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.post.return_value = {
                "exportId": "export-123",
                "status": "completed",
                "url": "https://download.example.com/image.jpg",
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["export_soracam_image"]
            result = tool.fn(device_id="ABC123DEF456", timestamp=1609459200000)

            assert result["export_id"] == "export-123"
            assert result["status"] == "completed"
            assert result["url"] == "https://download.example.com/image.jpg"

    def test_export_soracam_video_success(self) -> None:
        """export_soracam_video成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.post.return_value = {
                "exportId": "export-456",
                "status": "processing",
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["export_soracam_video"]
            result = tool.fn(
                device_id="ABC123DEF456",
                from_time=1609459200000,
                to_time=1609462800000,
            )

            assert result["export_id"] == "export-456"
            assert result["status"] == "processing"
            mock_client.post.assert_called_with(
                "/sora_cam/devices/ABC123DEF456/videos/exports",
                json={"from": 1609459200000, "to": 1609462800000},
            )

    def test_get_soracam_video_export_status_success(self) -> None:
        """get_soracam_video_export_status成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "exportId": "export-456",
                "status": "completed",
                "url": "https://download.example.com/video.mp4",
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["get_soracam_video_export_status"]
            result = tool.fn(device_id="ABC123DEF456", export_id="export-456")

            assert result["status"] == "completed"
            assert result["url"] == "https://download.example.com/video.mp4"

    def test_get_soracam_stream_url_success(self) -> None:
        """get_soracam_stream_url成功ケース"""
        with patch(
            "soracom_data_mcp.tools.soracam.soracom_client"
        ) as mock_client:
            mock_client.get.return_value = {
                "url": "https://stream.example.com/live",
                "expiresAt": 1609462800000,
            }
            mcp = FastMCP("test")
            register_soracam_tools(mcp)

            tool = mcp._tool_manager._tools["get_soracam_stream_url"]
            result = tool.fn(device_id="ABC123DEF456")

            assert result["url"] == "https://stream.example.com/live"
            assert result["expires_at"] == 1609462800000

