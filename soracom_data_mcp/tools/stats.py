"""SIM・統計情報ツール - SIM情報・通信統計取得"""

from typing import Any

from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError, handle_soracom_error, soracom_client


def register_stats_tools(mcp: FastMCP) -> None:
    """SIM・統計情報ツールを登録"""

    # ===================
    # SIM (Subscribers) API
    # ===================

    @mcp.tool()
    def list_subscribers(
        limit: int = 100,
        last_evaluated_key: str | None = None,
        status_filter: str | None = None,
        speed_class_filter: str | None = None,
        tag_name: str | None = None,
        tag_value: str | None = None,
        tag_value_match_mode: str = "exact",
    ) -> dict[str, Any]:
        """
        SIM一覧を取得します

        Args:
            limit: 取得件数（最大100）
            last_evaluated_key: ページング用キー
            status_filter: ステータスでフィルタ（active, inactive, ready, instock, shipped, suspended, terminated）
            speed_class_filter: 速度クラスでフィルタ
            tag_name: タグ名でフィルタ
            tag_value: タグ値でフィルタ
            tag_value_match_mode: タグ値の一致モード（exact, prefix）

        Returns:
            SIM一覧
        """
        try:
            params: dict[str, Any] = {
                "limit": min(limit, 100),
            }
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key
            if status_filter:
                params["status_filter"] = status_filter
            if speed_class_filter:
                params["speed_class_filter"] = speed_class_filter
            if tag_name:
                params["tag_name"] = tag_name
            if tag_value:
                params["tag_value"] = tag_value
                params["tag_value_match_mode"] = tag_value_match_mode

            response = soracom_client.get("/subscribers", params=params)

            if isinstance(response, list):
                subscribers = []
                for sub in response:
                    subscribers.append({
                        "imsi": sub.get("imsi"),
                        "msisdn": sub.get("msisdn"),
                        "iccid": sub.get("iccid"),
                        "status": sub.get("status"),
                        "speed_class": sub.get("speedClass"),
                        "tags": sub.get("tags", {}),
                        "group_id": sub.get("groupId"),
                        "subscription": sub.get("subscription"),
                    })
                return {
                    "subscribers": subscribers,
                    "count": len(subscribers),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_subscriber(imsi: str) -> dict[str, Any]:
        """
        特定SIMの詳細情報を取得します

        Args:
            imsi: SIMのIMSI

        Returns:
            SIM詳細情報
        """
        try:
            response = soracom_client.get(f"/subscribers/{imsi}")

            if isinstance(response, dict):
                return {
                    "imsi": response.get("imsi"),
                    "msisdn": response.get("msisdn"),
                    "iccid": response.get("iccid"),
                    "status": response.get("status"),
                    "speed_class": response.get("speedClass"),
                    "tags": response.get("tags", {}),
                    "group_id": response.get("groupId"),
                    "subscription": response.get("subscription"),
                    "module_type": response.get("moduleType"),
                    "plan": response.get("plan"),
                    "expiry_action": response.get("expiryAction"),
                    "created_at": response.get("createdAt"),
                    "last_modified_at": response.get("lastModifiedAt"),
                    "session_status": response.get("sessionStatus"),
                }

            return {"data": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    # ===================
    # Groups API
    # ===================

    @mcp.tool()
    def list_groups(
        limit: int = 100,
        last_evaluated_key: str | None = None,
        tag_name: str | None = None,
        tag_value: str | None = None,
        tag_value_match_mode: str = "exact",
    ) -> dict[str, Any]:
        """
        グループ一覧を取得します

        Args:
            limit: 取得件数
            last_evaluated_key: ページング用キー
            tag_name: タグ名でフィルタ
            tag_value: タグ値でフィルタ
            tag_value_match_mode: タグ値の一致モード（exact, prefix）

        Returns:
            グループ一覧
        """
        try:
            params: dict[str, Any] = {
                "limit": limit,
            }
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key
            if tag_name:
                params["tag_name"] = tag_name
            if tag_value:
                params["tag_value"] = tag_value
                params["tag_value_match_mode"] = tag_value_match_mode

            response = soracom_client.get("/groups", params=params)

            if isinstance(response, list):
                groups = []
                for group in response:
                    groups.append({
                        "group_id": group.get("groupId"),
                        "tags": group.get("tags", {}),
                        "created_at": group.get("createdAt"),
                        "last_modified_at": group.get("lastModifiedAt"),
                    })
                return {
                    "groups": groups,
                    "count": len(groups),
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_group(group_id: str) -> dict[str, Any]:
        """
        グループ詳細情報を取得します

        Args:
            group_id: グループID

        Returns:
            グループ詳細情報
        """
        try:
            response = soracom_client.get(f"/groups/{group_id}")

            if isinstance(response, dict):
                return {
                    "group_id": response.get("groupId"),
                    "tags": response.get("tags", {}),
                    "configuration": response.get("configuration", {}),
                    "created_at": response.get("createdAt"),
                    "last_modified_at": response.get("lastModifiedAt"),
                }

            return {"data": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    # ===================
    # Stats API
    # ===================

    @mcp.tool()
    def get_air_stats(
        imsi: str,
        from_time: int,
        to_time: int,
        period: str = "day",
    ) -> dict[str, Any]:
        """
        SIMの通信統計（Air利用量）を取得します

        Args:
            imsi: SIMのIMSI
            from_time: 取得開始時刻（UNIXタイムスタンプ・秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・秒）
            period: 集計期間（minutes, day, month）

        Returns:
            通信統計データ
        """
        try:
            params: dict[str, Any] = {
                "from": from_time,
                "to": to_time,
                "period": period,
            }

            response = soracom_client.get(
                f"/stats/air/subscribers/{imsi}", params=params
            )

            if isinstance(response, list):
                stats = []
                for stat in response:
                    stats.append({
                        "date": stat.get("date"),
                        "upload_bytes": stat.get("uploadByteSizeTotal"),
                        "download_bytes": stat.get("downloadByteSizeTotal"),
                        "upload_packets": stat.get("uploadPacketSizeTotal"),
                        "download_packets": stat.get("downloadPacketSizeTotal"),
                    })
                return {
                    "stats": stats,
                    "count": len(stats),
                    "imsi": imsi,
                    "period": period,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_harvest_stats(
        imsi: str,
        from_time: int,
        to_time: int,
        period: str = "day",
    ) -> dict[str, Any]:
        """
        SIMのHarvest利用統計を取得します

        Args:
            imsi: SIMのIMSI
            from_time: 取得開始時刻（UNIXタイムスタンプ・秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・秒）
            period: 集計期間（day, month）

        Returns:
            Harvest利用統計データ
        """
        try:
            params: dict[str, Any] = {
                "from": from_time,
                "to": to_time,
                "period": period,
            }

            response = soracom_client.get(
                f"/stats/harvest/subscribers/{imsi}", params=params
            )

            if isinstance(response, list):
                stats = []
                for stat in response:
                    stats.append({
                        "date": stat.get("date"),
                        "count": stat.get("count"),
                        "bytes": stat.get("bytes"),
                    })
                return {
                    "stats": stats,
                    "count": len(stats),
                    "imsi": imsi,
                    "period": period,
                }

            return response

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

