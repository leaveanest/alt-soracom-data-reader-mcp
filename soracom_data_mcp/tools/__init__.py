"""ツール登録ルーター - モードに応じてツールを登録"""

from typing import Literal

from fastmcp import FastMCP

from soracom_data_mcp.tools.harvest import register_harvest_tools
from soracom_data_mcp.tools.soracam import register_soracam_tools
from soracom_data_mcp.tools.stats import register_stats_tools

Mode = Literal["harvest", "soracam", "stats", "all"]


def register_tools(mcp: FastMCP, mode: Mode) -> None:
    """指定されたモードのツールを登録"""

    if mode in ("harvest", "all"):
        register_harvest_tools(mcp)

    if mode in ("soracam", "all"):
        register_soracam_tools(mcp)

    if mode in ("stats", "all"):
        register_stats_tools(mcp)

