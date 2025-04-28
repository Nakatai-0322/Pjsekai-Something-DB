import time
import requests
from bs4 import BeautifulSoup
import csv
from fugashi import GenericTagger  # TaggerではなくGenericTaggerを使用

# ふりがな生成関数
def get_furigana(text):
    tagger = GenericTagger()
    words = tagger.parse(text).splitlines()
    furigana = []
    for word in words:
        if word != "":  # 空行を無視
            try:
                surface, feature = word.split("\t")
                features = feature.split(",")
                if len(features) > 7:
                    furigana.append(features[7])  # ふりがなを取得
                else:
                    furigana.append(surface)  # ふりがながない場合はそのまま
            except ValueError:
                continue  # 解析結果が予期しない場合（例えば空行や異常な形式）はスキップ
    return "".join(furigana)

# URL設定
url = 'https://pjsekai.com/?aad6ee23b0'

# ページ取得
response = requests.get(url)
response.raise_for_status()

# HTML解析
soup = BeautifulSoup(response.text, 'html.parser')

# すべてのテーブルを探索、テーブル内の文字列を確認
lyrics = []
start_time = time.time()  # 処理時間の計測

# 特定の列を指定（例えば、1列目と3列目を抽出）
columns_to_extract = [3]  # 0が1列目、2が3列目を意味します

for table in soup.find_all('table'):  # 全てのテーブルを探索
    rows = table.find_all('tr')  # 各行（trタグ）
    for row in rows:
        columns = row.find_all('td')  # 各セル（tdタグ）
        
        # 指定した列のみ抽出
        for col_index in columns_to_extract:
            if col_index < len(columns):
                text = columns[col_index].get_text(strip=True)
                if text:  # 空のセルをスキップ
                    furigana = get_furigana(text)  # ふりがなを生成
                    lyrics.append([text, furigana])  # 歌詞とふりがなをペアにして追加

    # 処理時間の確認（ループが無限に回らないように制限）
    elapsed_time = time.time() - start_time
    if elapsed_time > 60:  # 60秒以上かかる場合、強制的に停止
        print("処理が遅すぎます。停止します。")
        break

# CSVに歌詞とふりがなを保存
with open('lyrics_with_furigana.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['歌詞', 'ふりがな'])  # ヘッダーを書き込む
    for lyric in lyrics:
        writer.writerow(lyric)

print(f"{len(lyrics)} 曲の歌詞とふりがなを lyrics_with_furigana.csv に保存しました。")
