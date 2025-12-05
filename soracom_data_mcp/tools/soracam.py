"""ソラカメ（SoraCam）ツール - クラウドカメラ映像・イベント取得"""

from typing import Any

from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError, handle_soracom_error, soracom_client


def register_soracam_tools(mcp: FastMCP) -> None:
    """ソラカメツールを登録"""

    # ===================
    # カメラ管理 API
    # ===================

    @mcp.tool()
    def list_soracam_devices(
        limit: int = 100,
        last_evaluated_key: str | None = None,
    ) -> dict[str, Any]:
        """
        ソラカメデバイス（カメラ）一覧を取得します

        Args:
            limit: 取得件数
            last_evaluated_key: ページング用キー

        Returns:
            カメラ一覧
        """
        try:
            params: dict[str, Any] = {
                "limit": limit,
            }
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key

            response = soracom_client.get("/sora_cam/devices", params=params)

            if isinstance(response, list):
                devices = []
                for device in response:
                    devices.append({
                        "device_id": device.get("deviceId"),
                        "name": device.get("name"),
                        "status": device.get("status"),
                        "connected": device.get("connected"),
                        "firmware_version": device.get("firmwareVersion"),
                    })
                return {
                    "devices": devices,
                    "count": len(devices),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_soracam_device(device_id: str) -> dict[str, Any]:
        """
        ソラカメデバイス（カメラ）の詳細情報を取得します

        Args:
            device_id: デバイスID

        Returns:
            カメラ詳細情報
        """
        try:
            response = soracom_client.get(f"/sora_cam/devices/{device_id}")

            if isinstance(response, dict):
                return {
                    "device_id": response.get("deviceId"),
                    "name": response.get("name"),
                    "status": response.get("status"),
                    "connected": response.get("connected"),
                    "firmware_version": response.get("firmwareVersion"),
                    "configuration": response.get("configuration"),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    # ===================
    # イベント検出 API
    # ===================

    @mcp.tool()
    def list_soracam_events(
        device_id: str,
        from_time: int | None = None,
        to_time: int | None = None,
        sort: str = "desc",
        limit: int = 100,
        last_evaluated_key: str | None = None,
    ) -> dict[str, Any]:
        """
        ソラカメのイベント（動体検知等）一覧を取得します

        Args:
            device_id: デバイスID
            from_time: 取得開始時刻（UNIXタイムスタンプ・ミリ秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・ミリ秒）
            sort: ソート順（asc: 古い順, desc: 新しい順）
            limit: 取得件数
            last_evaluated_key: ページング用キー

        Returns:
            イベント一覧
        """
        try:
            params: dict[str, Any] = {
                "sort": sort,
                "limit": limit,
            }
            if from_time is not None:
                params["from"] = from_time
            if to_time is not None:
                params["to"] = to_time
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key

            response = soracom_client.get(
                f"/sora_cam/devices/{device_id}/events", params=params
            )

            if isinstance(response, list):
                events = []
                for event in response:
                    events.append({
                        "event_id": event.get("eventId"),
                        "device_id": event.get("deviceId"),
                        "event_type": event.get("eventType"),
                        "timestamp": event.get("time"),
                    })
                return {
                    "events": events,
                    "count": len(events),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_soracam_event(device_id: str, event_id: str) -> dict[str, Any]:
        """
        ソラカメのイベント詳細を取得します

        Args:
            device_id: デバイスID
            event_id: イベントID

        Returns:
            イベント詳細情報
        """
        try:
            response = soracom_client.get(
                f"/sora_cam/devices/{device_id}/events/{event_id}"
            )

            if isinstance(response, dict):
                return {
                    "event_id": response.get("eventId"),
                    "device_id": response.get("deviceId"),
                    "event_type": response.get("eventType"),
                    "timestamp": response.get("time"),
                    "details": response,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    # ===================
    # 録画・静止画 API
    # ===================

    @mcp.tool()
    def list_soracam_videos(
        device_id: str,
        from_time: int | None = None,
        to_time: int | None = None,
    ) -> dict[str, Any]:
        """
        ソラカメの録画一覧を取得します

        Args:
            device_id: デバイスID
            from_time: 取得開始時刻（UNIXタイムスタンプ・ミリ秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・ミリ秒）

        Returns:
            録画一覧
        """
        try:
            params: dict[str, Any] = {}
            if from_time is not None:
                params["from"] = from_time
            if to_time is not None:
                params["to"] = to_time

            response = soracom_client.get(
                f"/sora_cam/devices/{device_id}/videos", params=params
            )

            if isinstance(response, list):
                return {
                    "videos": response,
                    "count": len(response),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def export_soracam_image(
        device_id: str,
        timestamp: int,
    ) -> dict[str, Any]:
        """
        ソラカメの静止画をエクスポートします

        Args:
            device_id: デバイスID
            timestamp: 取得したい時刻（UNIXタイムスタンプ・ミリ秒）

        Returns:
            静止画エクスポート情報（ダウンロードURL等）
        """
        try:
            response = soracom_client.post(
                f"/sora_cam/devices/{device_id}/videos/images",
                json={"time": timestamp},
            )

            if isinstance(response, dict):
                return {
                    "export_id": response.get("exportId"),
                    "status": response.get("status"),
                    "url": response.get("url"),
                    "details": response,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def export_soracam_video(
        device_id: str,
        from_time: int,
        to_time: int,
    ) -> dict[str, Any]:
        """
        ソラカメの録画動画をエクスポートします

        Args:
            device_id: デバイスID
            from_time: 開始時刻（UNIXタイムスタンプ・ミリ秒）
            to_time: 終了時刻（UNIXタイムスタンプ・ミリ秒）

        Returns:
            録画エクスポート情報（export_id等）
        """
        try:
            response = soracom_client.post(
                f"/sora_cam/devices/{device_id}/videos/exports",
                json={
                    "from": from_time,
                    "to": to_time,
                },
            )

            if isinstance(response, dict):
                return {
                    "export_id": response.get("exportId"),
                    "status": response.get("status"),
                    "details": response,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_soracam_video_export_status(
        device_id: str,
        export_id: str,
    ) -> dict[str, Any]:
        """
        ソラカメの録画エクスポート状況を取得します

        Args:
            device_id: デバイスID
            export_id: エクスポートID

        Returns:
            エクスポート状況（status, url等）
        """
        try:
            response = soracom_client.get(
                f"/sora_cam/devices/{device_id}/videos/exports/{export_id}"
            )

            if isinstance(response, dict):
                return {
                    "export_id": response.get("exportId"),
                    "status": response.get("status"),
                    "url": response.get("url"),
                    "details": response,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_soracam_stream_url(device_id: str) -> dict[str, Any]:
        """
        ソラカメのライブストリーミングURLを取得します

        Args:
            device_id: デバイスID

        Returns:
            ストリーミングURL
        """
        try:
            response = soracom_client.get(f"/sora_cam/devices/{device_id}/stream")

            if isinstance(response, dict):
                return {
                    "url": response.get("url"),
                    "expires_at": response.get("expiresAt"),
                    "details": response,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

