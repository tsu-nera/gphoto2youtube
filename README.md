# Google Photo to YouTube Uploader

Google Photo からダウンロードした動画を YouTube に限定公開でアップロードするツール

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. YouTube API の認証情報を取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（またはすでに存在するプロジェクトを選択）
3. 「API とサービス」→「ライブラリ」から「YouTube Data API v3」を有効化
4. 「API とサービス」→「認証情報」→「認証情報を作成」→「OAuth クライアント ID」を選択
5. アプリケーションの種類として「デスクトップアプリ」を選択
6. 作成された認証情報の JSON ファイルをダウンロード
7. ダウンロードした JSON ファイルを `client_secrets.json` という名前でこのディレクトリに配置

## 使い方

### 1. 動画の結合（オプション）

tmpフォルダ内の複数の動画をファイル名順（タイムスタンプ順）に結合する場合:

```bash
python concat_videos.py
```

#### ffmpeg のインストール

動画結合には ffmpeg が必要です:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

#### オプション

```bash
python concat_videos.py --input-dir tmp --output merged_video.mp4
```

- `--input-dir`: 動画があるディレクトリ（デフォルト: tmp）
- `--output`: 出力ファイル名（デフォルト: merged_video.mp4）
- `--keep-list`: 結合リストファイルを保持

### 2. YouTube へのアップロード

```bash
python upload_to_youtube.py <動画ファイルのパス>
```

### オプション

```bash
python upload_to_youtube.py <動画ファイル> --title "動画のタイトル" --description "動画の説明" --privacy private
```

- `--title`: 動画のタイトル（指定しない場合はファイル名を使用）
- `--description`: 動画の説明
- `--privacy`: 公開設定（`public`, `private`, `unlisted`のいずれか、デフォルト: `unlisted`）

### 例

```bash
# 限定公開動画としてアップロード（デフォルト）
python upload_to_youtube.py video.mp4

# タイトルと説明を指定してアップロード
python upload_to_youtube.py video.mp4 --title "私の動画" --description "テスト動画です"

# 非公開でアップロード
python upload_to_youtube.py video.mp4 --privacy private
```

## 初回実行時の認証

初回実行時にブラウザが開き、Google アカウントでのログインを求められます。
認証が完了すると、`token.pickle` ファイルが作成され、次回以降は自動的に認証されます。

## 注意事項

- YouTube API には1日あたりのアップロード上限があります
- `client_secrets.json` と `token.pickle` は機密情報なので、Git にコミットしないように `.gitignore` に追加してください
