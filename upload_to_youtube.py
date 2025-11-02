#!/usr/bin/env python3
"""
YouTube に動画を非公開でアップロードするスクリプト
"""

import os
import sys
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# YouTube API のスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """YouTube API の認証を行い、サービスオブジェクトを返す"""
    credentials = None

    # token.pickle ファイルが存在する場合は読み込む
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # 有効な認証情報がない場合は新規に取得
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=0)

        # 認証情報を保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_file, title, description='', category='22', privacy_status='private'):
    """
    YouTube に動画をアップロードする

    Args:
        youtube: YouTube API サービスオブジェクト
        video_file: アップロードする動画ファイルのパス
        title: 動画のタイトル
        description: 動画の説明
        category: カテゴリID (デフォルト: 22 = People & Blogs)
        privacy_status: 公開設定 ('public', 'private', 'unlisted')

    Returns:
        アップロードされた動画のID
    """
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    # 動画ファイルをアップロード
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    print(f'アップロード中: {video_file}')
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'進捗: {int(status.progress() * 100)}%')

    print(f'アップロード完了! 動画ID: {response["id"]}')
    print(f'URL: https://www.youtube.com/watch?v={response["id"]}')

    return response['id']

def main():
    parser = argparse.ArgumentParser(description='YouTube に動画をアップロード')
    parser.add_argument('video_file', help='アップロードする動画ファイル')
    parser.add_argument('--title', default=None, help='動画のタイトル (デフォルト: ファイル名)')
    parser.add_argument('--description', default='', help='動画の説明')
    parser.add_argument('--privacy', default='private',
                       choices=['public', 'private', 'unlisted'],
                       help='公開設定 (デフォルト: private)')

    args = parser.parse_args()

    # 動画ファイルの存在確認
    if not os.path.exists(args.video_file):
        print(f'エラー: ファイルが見つかりません: {args.video_file}')
        sys.exit(1)

    # タイトルが指定されていない場合はファイル名を使用
    title = args.title if args.title else os.path.splitext(os.path.basename(args.video_file))[0]

    try:
        # YouTube API 認証
        youtube = get_authenticated_service()

        # 動画をアップロード
        upload_video(
            youtube,
            args.video_file,
            title,
            args.description,
            privacy_status=args.privacy
        )

    except Exception as e:
        print(f'エラーが発生しました: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
