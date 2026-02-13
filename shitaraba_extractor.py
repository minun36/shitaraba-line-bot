"""
したらば掲示板からVALORANTスレッドとレスを取得するモジュール

必須関数:
 - get_latest_valorant_thread() -> dict | None
 - extract_post_bodies(thread_url: str) -> list[str]
 - clean_text(text: str) -> str

このファイルは設計書に従ってEUC-JPでデコードして処理します。
"""
from typing import Optional, List, Dict
import re
import requests
from bs4 import BeautifulSoup


SUBJECT_URL = "https://jbbs.shitaraba.net/bbs/subject.cgi/netgame/16797/"
BASE_URL = "https://jbbs.shitaraba.net"


def get_latest_valorant_thread() -> Optional[Dict]:
    """
    条件に合う最新のVALORANTスレッドを取得

    戻り値:
    {
        'name': 'VALORANT part1925(2763)',
        'url': 'https://jbbs.shitaraba.net/bbs/read.cgi/netgame/16797/...',
        'part': 1925,
        'posts': 2763
    }
    または None
    """
    try:
        resp = requests.get(SUBJECT_URL, timeout=10)
        resp.encoding = 'EUC-JP'
        soup = BeautifulSoup(resp.text, 'html.parser')

        candidates = []
        for a in soup.find_all('a', href=True):
            text = (a.get_text() or '').strip()
            m = re.match(r'VALORANT part(\d+)\((\d+)\)', text)
            if not m:
                continue
            part = int(m.group(1))
            posts = int(m.group(2))
            if posts < 300:
                continue
            href = a['href']
            # make absolute URL if necessary
            if href.startswith('/'): 
                url = BASE_URL + href
            else:
                url = href
            candidates.append({'name': text, 'url': url, 'part': part, 'posts': posts})

        if not candidates:
            return None

        # 最新 = part が最大
        latest = max(candidates, key=lambda x: x['part'])
        return latest

    except Exception as e:
        print(f"エラー: get_latest_valorant_thread(): {e}")
        return None


def extract_post_bodies(thread_url: str) -> List[str]:
    """
    スレッドURLから<dd>タグの本文を抽出してクリーンして返す

    戻り値: ['レス1本文', 'レス2本文', ...]
    失敗時は空リストを返す
    """
    try:
        resp = requests.get(thread_url, timeout=10)
        resp.encoding = 'EUC-JP'
        soup = BeautifulSoup(resp.text, 'html.parser')

        posts: List[str] = []
        for dd in soup.find_all('dd'):
            text = dd.get_text(separator=' ')
            cleaned = clean_text(text)
            if cleaned:
                posts.append(cleaned)

        return posts

    except Exception as e:
        print(f"エラー: extract_post_bodies(): {e}")
        return []


def clean_text(text: str) -> str:
    """
    レステキストから不要要素を除去する

    処理:
    1. アンカー除去: >>123, >>123-456
    2. URL除去
    3. 連続空白を1つに
    4. 前後の空白を削除
    """
    if text is None:
        return ''
    # アンカー除去
    text = re.sub(r'>>\d+(-\d+)?', '', text)
    # URL除去
    text = re.sub(r'https?://[^\s]+', '', text)
    # 全角/半角改行やタブをスペースに
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


if __name__ == '__main__':
    # 簡単な動作確認用
    t = get_latest_valorant_thread()
    print(t)
    if t:
        posts = extract_post_bodies(t['url'])
        print(f"取得したレス数: {len(posts)}")
