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


def _normalize_thread_url(thread_url: str) -> str:
    """スレッドURLを正規化して、余分なページ指定や末尾の数字を取り除く

    例: https://.../read.cgi/netgame/16797/1748243747/50 -> https://.../read.cgi/netgame/16797/1748243747/
    """
    if not thread_url:
        return thread_url
    # remove query
    url = thread_url.split('?', 1)[0]
    # ensure trailing slash
    if not url.endswith('/'):
        url = url + '/'
    # remove trailing page numbers after thread id, e.g. /.../1748243747/50 -> keep up to thread id
    m = re.match(r'(.*/bbs/read\.cgi/[^/]+/\d+/)(?:\d+/)?', url)
    if m:
        return m.group(1)
    return url


def extract_post_bodies(thread_url: str, expected_posts: Optional[int] = None) -> List[str]:
    """
    スレッドURLから<dd>タグの本文を抽出してクリーンして返す

    戻り値: ['レス1本文', 'レス2本文', ...]
    失敗時は空リストを返す
    """
    try:
        url_candidates = []
        # normalized base url
        base = _normalize_thread_url(thread_url)
        url_candidates.append(base)
        # 一部ページでは '?mode=all' 等で全件表示できる場合がある
        url_candidates.append(base + '?mode=all')
        url_candidates.append(base + 'index.html')

        posts: List[str] = []
        for url in url_candidates:
            try:
                resp = requests.get(url, timeout=10)
                resp.encoding = 'EUC-JP'
                soup = BeautifulSoup(resp.text, 'html.parser')
                found = []
                for dd in soup.find_all('dd'):
                    text = dd.get_text(separator=' ')
                    cleaned = clean_text(text)
                    if cleaned:
                        found.append(cleaned)

                # 見つかった件数が期待値に近い、または十分に多ければ採用
                if expected_posts and len(found) >= min(50, expected_posts):
                    posts = found
                    break
                # 期待値が与えられていない場合は最も多く見つかったものを採用
                if not expected_posts and len(found) > len(posts):
                    posts = found
            except Exception as inner_e:
                print(f"警告: extract_post_bodies() 内の候補URL取得失敗 {url}: {inner_e}")
                continue

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
