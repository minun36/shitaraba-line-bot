import re
import requests
from bs4 import BeautifulSoup


def get_latest_valorant_thread() -> dict | None:
    """
    条件に合う最新のVALORANTスレッドを取得
    
    処理フロー:
    1. https://jbbs.shitaraba.net/bbs/subject.cgi/netgame/16797/ にアクセス
    2. HTMLをEUC-JPでデコード
    3. <a>タグからスレッド一覧を取得
    4. 正規表現で「VALORANT part(\d+)\((\d+)\)」にマッチするものを抽出
    5. レス数が300以上のものをフィルタ
    6. パート番号が最大のものを返す
    
    戻り値:
    {
        'name': 'VALORANT part1925(2763)',
        'url': 'https://jbbs.shitaraba.net/bbs/read.cgi/netgame/16797/...',
        'part': 1925,
        'posts': 2763
    }
    または None（該当なし）
    """
    try:
        url = "https://jbbs.shitaraba.net/bbs/subject.cgi/netgame/16797/"
        response = requests.get(url, timeout=10)
        # したらば掲示板は EUC-JP を使用
        response.encoding = 'EUC-JP'
        html = response.text
        
        # HTMLをパース
        soup = BeautifulSoup(html, 'html.parser')
        
        # <a>タグからスレッド一覧を取得
        threads = []
        for link in soup.find_all('a'):
            thread_name = link.get_text(strip=True)
            thread_url = link.get('href', '')
            
            # 正規表現で「VALORANT part(\d+)\((\d+)\)」にマッチするかチェック
            match = re.match(r'VALORANT part(\d+)\((\d+)\)', thread_name)
            if match:
                part_num = int(match.group(1))
                post_count = int(match.group(2))
                
                # レス数が300以上のもののみフィルタ
                if post_count >= 300:
                    # URLを完全なパスに変換
                    if thread_url.startswith('/'):
                        full_url = f"https://jbbs.shitaraba.net{thread_url}"
                    else:
                        full_url = thread_url
                    
                    threads.append({
                        'name': thread_name,
                        'url': full_url,
                        'part': part_num,
                        'posts': post_count
                    })
        
        # パート番号が最大のものを返す
        if threads:
            latest_thread = max(threads, key=lambda x: x['part'])
            return latest_thread
        else:
            return None
            
    except Exception as e:
        print(f"エラー: スレッド取得に失敗 - {e}")
        return None


def extract_post_bodies(thread_url: str) -> list[str]:
    """
    スレッドURLからレス本文のみを抽出
    
    処理フロー:
    1. スレッドURLにアクセス
    2. HTMLをEUC-JPでデコード
    3. <dd>タグをすべて取得
    4. 各<dd>のテキストをclean_text()で整形
    5. 空でないもののみリストに追加
    
    戻り値: ['レス1本文', 'レス2本文', ...]
    """
    try:
        response = requests.get(thread_url, timeout=10)
        # したらば掲示板は EUC-JP を使用
        response.encoding = 'EUC-JP'
        html = response.text
        
        # HTMLをパース
        soup = BeautifulSoup(html, 'html.parser')
        
        # <dd>タグをすべて取得
        posts = []
        for dd_tag in soup.find_all('dd'):
            text = dd_tag.get_text(strip=False)
            # ホワイトスペースを正規化
            text = re.sub(r'\n', ' ', text)
            # テキストをクリーニング
            cleaned_text = clean_text(text)
            # 空でないもののみリストに追加
            if cleaned_text:
                posts.append(cleaned_text)
        
        return posts
        
    except Exception as e:
        print(f"エラー: レス取得に失敗 - {e}")
        return []


def clean_text(text: str) -> str:
    """
    レステキストから不要要素を除去
    
    処理:
    1. アンカー除去: re.sub(r'>>\d+(-\d+)?', '', text)
    2. URL除去: re.sub(r'https?://[^\s]+', '', text)
    3. 連続空白を1つに: re.sub(r'\s+', ' ', text)
    4. 前後の空白を削除: text.strip()
    
    戻り値: クリーニング済みテキスト
    """
    # アンカーを除去（>>123 や >>123-456 のような形式）
    text = re.sub(r'>>\d+(-\d+)?', '', text)
    
    # URLを除去（http://... や https://...）
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # 連続する空白を1つに
    text = re.sub(r'\s+', ' ', text)
    
    # 前後の空白を削除
    text = text.strip()
    
    return text
