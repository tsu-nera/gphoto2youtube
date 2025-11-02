#!/usr/bin/env python3
"""
tmpフォルダ内の複数動画をファイル名順に結合するスクリプト
（Google Photoからダウンロードした動画のタイムスタンプ順に対応）
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# サポートする動画形式
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv', '.wmv'}

def find_videos(directory):
    """
    指定されたディレクトリ内の動画ファイルを検索

    Args:
        directory: 検索するディレクトリのパス

    Returns:
        動画ファイルのPathオブジェクトのリスト
    """
    video_files = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f'エラー: ディレクトリが見つかりません: {directory}')
        return []

    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)

    return video_files

def sort_videos_by_name(video_files):
    """
    動画ファイルをファイル名順にソート（タイムスタンプが含まれる場合に対応）

    Args:
        video_files: 動画ファイルのPathオブジェクトのリスト

    Returns:
        ソートされた動画ファイルのリスト
    """
    # ファイル名順にソート
    sorted_files = sorted(video_files, key=lambda x: x.name)

    # ソート結果を表示
    print('結合する動画ファイル（ファイル名順）:')
    for i, file_path in enumerate(sorted_files, 1):
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f'  {i}. {file_path.name} (更新日時: {mtime.strftime("%Y-%m-%d %H:%M:%S")})')

    return sorted_files

def create_concat_file(video_files, concat_file='concat_list.txt'):
    """
    ffmpeg用の結合リストファイルを作成

    Args:
        video_files: 動画ファイルのリスト
        concat_file: 作成するリストファイルのパス
    """
    with open(concat_file, 'w', encoding='utf-8') as f:
        for video_file in video_files:
            # 絶対パスを使用し、シングルクォートでエスケープ
            abs_path = video_file.resolve()
            f.write(f"file '{abs_path}'\n")

    print(f'\n結合リストファイルを作成しました: {concat_file}')

def concat_videos(concat_file, output_file):
    """
    ffmpegを使用して動画を結合

    Args:
        concat_file: 結合リストファイルのパス
        output_file: 出力ファイルのパス
    """
    # ffmpegがインストールされているか確認
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('エラー: ffmpegがインストールされていません')
        print('以下のコマンドでインストールしてください:')
        print('  Ubuntu/Debian: sudo apt-get install ffmpeg')
        print('  macOS: brew install ffmpeg')
        sys.exit(1)

    # ffmpegで動画を結合
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',  # 再エンコードせずにコピー（高速）
        output_file
    ]

    print(f'\n動画を結合中...')
    print(f'出力ファイル: {output_file}')

    try:
        subprocess.run(cmd, check=True)
        print(f'\n✓ 結合が完了しました: {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'\nエラー: 動画の結合に失敗しました')
        print(f'詳細: {e}')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='tmpフォルダ内の動画をファイル名順に結合'
    )
    parser.add_argument(
        '--input-dir',
        default='tmp',
        help='動画ファイルがあるディレクトリ (デフォルト: tmp)'
    )
    parser.add_argument(
        '--output',
        default='merged_video.mp4',
        help='出力ファイル名 (デフォルト: merged_video.mp4)'
    )
    parser.add_argument(
        '--keep-list',
        action='store_true',
        help='結合リストファイルを削除せずに保持'
    )

    args = parser.parse_args()

    # 動画ファイルを検索
    print(f'ディレクトリを検索中: {args.input_dir}')
    video_files = find_videos(args.input_dir)

    if not video_files:
        print(f'動画ファイルが見つかりませんでした')
        print(f'サポートされている形式: {", ".join(VIDEO_EXTENSIONS)}')
        sys.exit(1)

    print(f'\n{len(video_files)} 個の動画ファイルが見つかりました\n')

    # ファイル名順にソート
    sorted_videos = sort_videos_by_name(video_files)

    # 結合リストファイルを作成
    concat_list_file = 'concat_list.txt'
    create_concat_file(sorted_videos, concat_list_file)

    # 動画を結合
    concat_videos(concat_list_file, args.output)

    # 結合リストファイルを削除
    if not args.keep_list:
        os.remove(concat_list_file)
        print(f'結合リストファイルを削除しました: {concat_list_file}')

if __name__ == '__main__':
    main()
