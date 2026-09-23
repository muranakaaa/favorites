# favorites

Xのお気に入り投稿とSpotifyのプレイリストをまとめた1ページ。GitHub Pages で公開している。

https://muranakaaa.github.io/favorites/

## 構成

- `posts.json` — 投稿データ（本文・日付・写真のファイル名とサイズ）
- `images/` — 投稿の写真。`<投稿ID>-<連番>.jpg`
- `template.html` — ページの雛形。CSS と ライトボックスの JS もここ
- `build.py` — `posts.json` + `template.html` から `index.html` を生成する。プレイリストのIDと名前もここ

## 投稿を足す

1. 取得する（`<id>` は投稿URL末尾の数字）

```
curl -sL "https://cdn.syndication.twimg.com/tweet-result?id=<id>&lang=ja&token=a<id>"
```

2. 本文・日付・写真を `posts.json` に追記し、写真を `images/` に置く
3. `python3 build.py` で `index.html` を作り直す
