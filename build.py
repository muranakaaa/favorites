"""posts.json と images/ から index.html を生成する。"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
SITE_TITLE = "村中のお気に入りの投稿"
SITE_DESCRIPTION = "旅と街歩きの記録。港町・喫茶店・商店街・ローカル線。"
SITE_URL = "https://muranakaaa.github.io/favorites/"
OGP_IMAGE = "images/2050552757766304211-1.jpg"
HANDLE = "ayatakaa_chan"
PLAYLIST_ID = "2XhVxvRuQOpO572VeJgils"
PLAYLIST_NAME = "私を構成する42枚（洋楽）"


def format_date(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{year}年{int(month)}月{int(day)}日"


def linkify(text: str) -> str:
    escaped = html.escape(text)
    return escaped.replace("\n", "<br>")


def media_class(count: int) -> str:
    return {1: "m1", 2: "m2", 3: "m3"}.get(count, "m4")


def render_media(post: dict) -> str:
    media = post["media"]
    if not media:
        return ""
    items = []
    for index, m in enumerate(media):
        items.append(
            f'<button class="shot" type="button" data-post="{post["id"]}" data-index="{index}">'
            f'<img src="images/{m["file"]}" width="{m["w"]}" height="{m["h"]}"'
            f' loading="lazy" decoding="async" alt=""></button>'
        )
    return f'<div class="media {media_class(len(media))}">{"".join(items)}</div>'


def render_post(post: dict) -> str:
    url = f"https://x.com/{HANDLE}/status/{post['id']}"
    return f"""<article class="post">
<p class="text">{linkify(post["text"])}</p>
{render_media(post)}
<footer class="meta">
<time datetime="{post["date"]}">{format_date(post["date"])}</time>
<a href="{url}" target="_blank" rel="noopener">Xで見る</a>
</footer>
</article>"""


def main() -> None:
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    posts.sort(key=lambda p: p["date"], reverse=True)

    feed = "\n".join(render_post(p) for p in posts)
    lightbox_data = json.dumps(
        {p["id"]: [{"src": f"images/{m['file']}", "w": m["w"], "h": m["h"]} for m in p["media"]] for p in posts},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    template = (ROOT / "template.html").read_text(encoding="utf-8")
    output = (
        template.replace("{{TITLE}}", SITE_TITLE)
        .replace("{{DESCRIPTION}}", SITE_DESCRIPTION)
        .replace("{{URL}}", SITE_URL)
        .replace("{{OGP_IMAGE}}", OGP_IMAGE)
        .replace("{{HANDLE}}", HANDLE)
        .replace("{{COUNT}}", str(len(posts)))
        .replace("{{PLAYLIST_ID}}", PLAYLIST_ID)
        .replace("{{PLAYLIST_NAME}}", PLAYLIST_NAME)
        .replace("{{FEED}}", feed)
        .replace("{{LIGHTBOX_DATA}}", lightbox_data)
    )
    (ROOT / "index.html").write_text(output, encoding="utf-8")
    print(f"index.html: {len(posts)} posts, {sum(len(p['media']) for p in posts)} photos")


if __name__ == "__main__":
    main()
