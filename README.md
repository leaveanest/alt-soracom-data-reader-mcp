# SORACOM データ分析 MCP

SORACOM APIを活用したデータ分析向けMCP（Model Context Protocol）サーバーです。

## 概要

SORACOM Harvest Data、Harvest Files、ソラカメのデータを取得・分析するためのツールを提供します。
認証にはSAMユーザーの認証キーを使用します。

## 対象API一覧

### 1. Harvest Data（センサーデータ）📊

| API                                                    | 説明                        | モード    |
| ------------------------------------------------------ | --------------------------- | --------- |
| `GET /v1/data/subscribers/{imsi}`                      | 特定SIMのHarvest Dataを取得 | `harvest` |
| `GET /v1/data/resources/{resource_type}/{resource_id}` | リソース単位でデータ取得    | `harvest` |

### 2. Harvest Files（ファイルストレージ）📁

| API                            | 説明                                    | モード    |
| ------------------------------ | --------------------------------------- | --------- |
| `GET /v1/files/{scope}/{path}` | ファイル・ディレクトリ一覧取得          | `harvest` |
| `GET /v1/files/{scope}/{path}` | ファイルダウンロード（`redirect=true`） | `harvest` |
| `GET /v1/files/{scope}/_info`  | ストレージ使用状況                      | `harvest` |

### 3. ソラカメ - カメラ管理（SoraCam Devices）📹

| API                                    | 説明               | モード    |
| -------------------------------------- | ------------------ | --------- |
| `GET /v1/sora_cam/devices`             | カメラ一覧取得     | `soracam` |
| `GET /v1/sora_cam/devices/{device_id}` | カメラ詳細情報取得 | `soracam` |

### 4. ソラカメ - 録画・静止画（SoraCam Videos）🎬

| API                                                               | 説明                  | モード    |
| ----------------------------------------------------------------- | --------------------- | --------- |
| `GET /v1/sora_cam/devices/{device_id}/videos`                     | 録画一覧取得          | `soracam` |
| `POST /v1/sora_cam/devices/{device_id}/videos/exports`            | 録画エクスポート開始  | `soracam` |
| `GET /v1/sora_cam/devices/{device_id}/videos/exports/{export_id}` | エクスポート状況確認  | `soracam` |
| `POST /v1/sora_cam/devices/{device_id}/videos/images`             | 静止画取得            | `soracam` |
| `GET /v1/sora_cam/devices/{device_id}/stream`                     | ストリーミングURL取得 | `soracam` |

### 5. ソラカメ - イベント検出（SoraCam Events）🔔

| API                                                      | 説明             | モード    |
| -------------------------------------------------------- | ---------------- | --------- |
| `GET /v1/sora_cam/devices/{device_id}/events`            | イベント一覧取得 | `soracam` |
| `GET /v1/sora_cam/devices/{device_id}/events/{event_id}` | イベント詳細取得 | `soracam` |

### 6. SIM・統計情報（Subscribers & Stats）📈

| API                                    | 説明                        | モード  |
| -------------------------------------- | --------------------------- | ------- |
| `GET /v1/subscribers`                  | SIM一覧取得                 | `stats` |
| `GET /v1/subscribers/{imsi}`           | 特定SIM情報取得             | `stats` |
| `GET /v1/groups`                       | グループ一覧取得            | `stats` |
| `GET /v1/stats/air/subscribers/{imsi}` | SIM通信統計（データ使用量） | `stats` |
| `GET /v1/stats/harvest/{imsi}`         | Harvest利用統計             | `stats` |

## 認証の設定

このMCPを使用するには、SORACOM SAMユーザーの認証キーを取得する必要があります。

### 認証キーの取得方法

1. [SORACOMユーザーコンソール](https://console.soracom.io/) にログイン
2. 右上のアカウントメニュー → 「セキュリティ」を選択
3. 「SAMユーザー」タブを選択
4. SAMユーザーを作成（または既存のユーザーを選択）
5. 「認証キー」を生成
6. `authKeyId` と `authKey` をメモ

### 必要な権限

SAMユーザーには以下の権限が必要です：

- `harvest:getDataEntry` - Harvest Data読み取り
- `files:getObject` - Harvest Files読み取り
- `files:listObjects` - Harvest Files一覧取得
- `SoraCam:*` - ソラカメ操作（必要に応じて絞り込み可）
- `subscriber:getSubscriber` - SIM情報読み取り
- `stats:getAirStats` - 通信統計読み取り

## 使い方

### インストール

```bash
# GitHubから直接インストール
uv tool install git+https://github.com/xxx/soracom-data-mcp.git

# 実行
soracom-data-mcp --mode harvest
```

```bash
# または、uvxで一時的に実行（インストール不要）
uvx --from git+https://github.com/xxx/soracom-data-mcp.git soracom-data-mcp --mode harvest
```

### モード

| モード    | 説明                       |
| --------- | -------------------------- |
| `harvest` | Harvest Data/Files取得     |
| `soracam` | ソラカメ映像・イベント取得 |
| `stats`   | SIM情報・通信統計取得      |
| `all`     | 全ツール（開発用）         |

### 環境変数

```bash
export SORACOM_AUTH_KEY_ID="keyId-xxx"  # 必須
export SORACOM_AUTH_KEY="secret-xxx"    # 必須
export SORACOM_COVERAGE="jp"            # オプション（デフォルト: jp）
```

### MCP設定例

#### uv tool installでインストール済みの場合

```json
{
  "mcpServers": {
    "soracom-harvest": {
      "command": "soracom-data-mcp",
      "args": ["--mode", "harvest"],
      "env": {
        "SORACOM_AUTH_KEY_ID": "keyId-xxx",
        "SORACOM_AUTH_KEY": "secret-xxx"
      }
    }
  }
}
```

#### uvxでGitHubから直接実行

```json
{
  "mcpServers": {
    "soracom-harvest": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/xxx/soracom-data-mcp.git",
        "soracom-data-mcp", "--mode", "harvest"
      ],
      "env": {
        "SORACOM_AUTH_KEY_ID": "keyId-xxx",
        "SORACOM_AUTH_KEY": "secret-xxx"
      }
    }
  }
}
```

#### ローカル開発用

```json
{
  "mcpServers": {
    "soracom-harvest": {
      "command": "uv",
      "args": ["run", "soracom-data-mcp", "--mode", "harvest"],
      "env": {
        "SORACOM_AUTH_KEY_ID": "keyId-xxx",
        "SORACOM_AUTH_KEY": "secret-xxx"
      }
    }
  }
}
```

## 注意事項

- APIにはレート制限があります
- ソラカメAPIはソラカメ契約が必要です
- Harvest Data/FilesはHarvest契約が必要です

## 参考リンク

- [SORACOM API リファレンス](https://users.soracom.io/ja-jp/tools/api/reference/)
- [Harvest Data API ドキュメント](https://users.soracom.io/ja-jp/docs/harvest/get-data/)
- [ソラカメ API 公式ページ](https://soracom.jp/sora_cam/api/)
- [ソラカメ API の使いかた](https://users.soracom.io/ja-jp/docs/soracom-cloud-camera-services/about-api-examples/)
