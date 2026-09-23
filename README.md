# favorites

村中の自己紹介ページ「むらなか待合室」。GitHub Pages で公開している。

https://muranakaaa.github.io/favorites/

## 構成

- `data/site.json` — サイト名・駅名標・お知らせ・自己紹介・興味関心・プレイリスト・ほしい物リスト
- `data/posts.json` — Xの投稿（本文・日付・写真のファイル名とサイズ）
- `images/` — 投稿の写真。`<投稿ID>-<連番>.jpg`
- `template.html` — ページの雛形。CSS と JS（写真の全画面表示・訪問カウンター）もここ
- `build.py` — `data/` と `template.html` から `index.html` を生成する

## 更新する

1. `data/` の該当ファイルを書き換える。番線の追加・順序は `build.py` の `platforms`
2. `python3 build.py`
3. commit して push する。Pages が `main` の `/` をそのまま配信する

## 投稿を足す

1. 取得する（`<id>` は投稿URL末尾の数字）

```
curl -sL "https://cdn.syndication.twimg.com/tweet-result?id=<id>&lang=ja&token=a<id>"
```

2. 本文・日付・写真を `data/posts.json` に追記し、写真を `images/` に置く（`?format=jpg&name=medium` で取る）
3. `python3 build.py`
