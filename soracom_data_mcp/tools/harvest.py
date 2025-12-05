"""Harvest Data/Files ツール - センサーデータ・ファイルストレージ取得"""

from typing import Any

from fastmcp import FastMCP

from soracom_data_mcp.client import SoracomApiError, handle_soracom_error, soracom_client


def register_harvest_tools(mcp: FastMCP) -> None:
    """Harvest Data/Files ツールを登録"""

    # ===================
    # Harvest Data API
    # ===================

    @mcp.tool()
    def get_harvest_data(
        imsi: str,
        from_time: int | None = None,
        to_time: int | None = None,
        sort: str = "desc",
        limit: int = 100,
        last_evaluated_key: str | None = None,
    ) -> dict[str, Any]:
        """
        特定SIMのHarvest Dataを取得します

        Args:
            imsi: SIMのIMSI
            from_time: 取得開始時刻（UNIXタイムスタンプ・ミリ秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・ミリ秒）
            sort: ソート順（asc: 古い順, desc: 新しい順）
            limit: 取得件数（最大1000）
            last_evaluated_key: ページング用キー

        Returns:
            Harvest Dataのリストと次ページのキー
        """
        try:
            params: dict[str, Any] = {
                "sort": sort,
                "limit": min(limit, 1000),
            }
            if from_time is not None:
                params["from"] = from_time
            if to_time is not None:
                params["to"] = to_time
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key

            response = soracom_client.get(f"/data/subscribers/{imsi}", params=params)

            # レスポンスがリストの場合
            if isinstance(response, list):
                return {
                    "data": response,
                    "count": len(response),
                }

            return {"data": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_harvest_data_by_resource(
        resource_type: str,
        resource_id: str,
        from_time: int | None = None,
        to_time: int | None = None,
        sort: str = "desc",
        limit: int = 100,
        last_evaluated_key: str | None = None,
    ) -> dict[str, Any]:
        """
        リソースタイプとIDでHarvest Dataを取得します

        Args:
            resource_type: リソースタイプ（subscriber, device など）
            resource_id: リソースID
            from_time: 取得開始時刻（UNIXタイムスタンプ・ミリ秒）
            to_time: 取得終了時刻（UNIXタイムスタンプ・ミリ秒）
            sort: ソート順（asc: 古い順, desc: 新しい順）
            limit: 取得件数（最大1000）
            last_evaluated_key: ページング用キー

        Returns:
            Harvest Dataのリストと次ページのキー
        """
        try:
            params: dict[str, Any] = {
                "sort": sort,
                "limit": min(limit, 1000),
            }
            if from_time is not None:
                params["from"] = from_time
            if to_time is not None:
                params["to"] = to_time
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key

            response = soracom_client.get(
                f"/data/resources/{resource_type}/{resource_id}", params=params
            )

            if isinstance(response, list):
                return {
                    "data": response,
                    "count": len(response),
                }

            return {"data": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    # ===================
    # Harvest Files API
    # ===================

    @mcp.tool()
    def list_harvest_files(
        scope: str = "private",
        path: str = "/",
        limit: int = 100,
        last_evaluated_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Harvest Filesのファイル・ディレクトリ一覧を取得します

        Args:
            scope: スコープ（private または operators/{operator_id}）
            path: パス（デフォルト: /）
            limit: 取得件数
            last_evaluated_key: ページング用キー

        Returns:
            ファイル・ディレクトリ一覧
        """
        try:
            params: dict[str, Any] = {
                "limit": limit,
            }
            if last_evaluated_key:
                params["last_evaluated_key"] = last_evaluated_key

            # パスの先頭の / を除去（APIは / なしで受け取る）
            normalized_path = path.lstrip("/")
            if normalized_path:
                endpoint = f"/files/{scope}/{normalized_path}"
            else:
                endpoint = f"/files/{scope}"

            response = soracom_client.get(endpoint, params=params)

            if isinstance(response, list):
                return {
                    "files": response,
                    "count": len(response),
                }

            return {"data": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_harvest_file_info(scope: str = "private") -> dict[str, Any]:
        """
        Harvest Filesのストレージ使用状況を取得します

        Args:
            scope: スコープ（private または operators/{operator_id}）

        Returns:
            ストレージ使用状況（使用量、ファイル数など）
        """
        try:
            response = soracom_client.get(f"/files/{scope}/_info")

            if isinstance(response, dict):
                return response

            return {"info": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

    @mcp.tool()
    def get_harvest_file_download_url(
        scope: str,
        path: str,
    ) -> dict[str, Any]:
        """
        Harvest Filesのファイルダウンロード用URLを取得します

        Args:
            scope: スコープ（private または operators/{operator_id}）
            path: ファイルパス

        Returns:
            ダウンロード用URL（リダイレクトURL）
        """
        try:
            # パスの先頭の / を除去
            normalized_path = path.lstrip("/")
            endpoint = f"/files/{scope}/{normalized_path}"

            # redirect=false でURLを取得
            response = soracom_client.get(endpoint, params={"redirect": "false"})

            if isinstance(response, dict):
                return response

            return {"url": response}

        except SoracomApiError as e:
            return {"error": handle_soracom_error(e)}

