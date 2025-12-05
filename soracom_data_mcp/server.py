"""MCPサーバー本体"""

import argparse

from fastmcp import FastMCP

from soracom_data_mcp.tools import Mode, register_tools

# モードの説明
MODE_DESCRIPTIONS = {
    "harvest": "Harvest Data/Files取得",
    "soracam": "ソラカメ映像・イベント取得",
    "stats": "SIM情報・通信統計取得",
    "all": "全ツール（開発用）",
}


def create_server(mode: Mode) -> FastMCP:
    """MCPサーバーを作成"""
    description = MODE_DESCRIPTIONS.get(mode, "SORACOMデータ分析MCP")
    mcp = FastMCP(
        name=f"soracom-data-mcp ({mode})",
        instructions=f"SORACOMデータ分析用MCPサーバー - {description}",
    )

    # モードに応じたツールを登録
    register_tools(mcp, mode)

    return mcp


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="SORACOM データ分析 MCP - SORACOMデータ分析向けMCPサーバー"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["harvest", "soracam", "stats", "all"],
        default="harvest",
        help="有効にするツールのモード (default: harvest)",
    )
    return parser.parse_args()


def main() -> None:
    """エントリーポイント"""
    args = parse_args()
    mode: Mode = args.mode

    mcp = create_server(mode)
    mcp.run()


if __name__ == "__main__":
    main()

