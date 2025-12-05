"""共有フィクスチャ"""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomClient


@pytest.fixture
def mock_soracom_client() -> Generator[MagicMock, None, None]:
    """モック化されたSoracomClientを提供"""
    with patch("soracom_data_mcp.client.soracom_client") as mock:
        mock.get = MagicMock()
        mock.post = MagicMock()
        yield mock


@pytest.fixture
def mock_httpx_client() -> Generator[MagicMock, None, None]:
    """モック化されたhttpx.Clientを提供"""
    with patch("httpx.Client") as mock:
        yield mock


@pytest.fixture
def soracom_client_instance() -> SoracomClient:
    """新しいSoracomClientインスタンスを提供"""
    return SoracomClient()


@pytest.fixture
def mcp_app() -> FastMCP:
    """FastMCPアプリインスタンスを提供"""
    return FastMCP("test-app")


@pytest.fixture
def sample_subscriber_response() -> list[dict[str, Any]]:
    """サンプルSIMレスポンスデータ"""
    return [
        {
            "imsi": "440103012345678",
            "msisdn": "818012345678",
            "iccid": "8981100000000000001",
            "status": "active",
            "speedClass": "s1.standard",
            "tags": {"name": "TestSIM"},
            "groupId": "group-12345",
            "subscription": "plan-D",
        }
    ]


@pytest.fixture
def sample_group_response() -> list[dict[str, Any]]:
    """サンプルグループレスポンスデータ"""
    return [
        {
            "groupId": "group-12345",
            "tags": {"name": "TestGroup"},
            "createdAt": 1609459200000,
            "lastModifiedAt": 1609459200000,
        }
    ]


@pytest.fixture
def sample_harvest_data_response() -> list[dict[str, Any]]:
    """サンプルHarvest Dataレスポンス"""
    return [
        {
            "time": 1609459200000,
            "contentType": "application/json",
            "content": {"temperature": 25.5, "humidity": 60},
        }
    ]


@pytest.fixture
def sample_soracam_device_response() -> list[dict[str, Any]]:
    """サンプルSoraCamデバイスレスポンス"""
    return [
        {
            "deviceId": "ABC123DEF456",
            "name": "TestCamera",
            "status": "active",
            "connected": True,
            "firmwareVersion": "1.0.0",
        }
    ]


@pytest.fixture
def sample_soracam_event_response() -> list[dict[str, Any]]:
    """サンプルSoraCamイベントレスポンス"""
    return [
        {
            "eventId": "event-12345",
            "deviceId": "ABC123DEF456",
            "eventType": "atomCamPersonDetected",
            "time": 1609459200000,
        }
    ]


@pytest.fixture
def sample_air_stats_response() -> list[dict[str, Any]]:
    """サンプルAir統計レスポンス"""
    return [
        {
            "date": "2024-01-01",
            "uploadByteSizeTotal": 1000,
            "downloadByteSizeTotal": 2000,
            "uploadPacketSizeTotal": 10,
            "downloadPacketSizeTotal": 20,
        }
    ]

