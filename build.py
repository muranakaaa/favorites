"""data/ と images/ から index.html を生成する。"""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def read_json(name: str) -> dict | list:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def format_date(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{year}.{int(month):02d}.{int(day):02d}"


def section(slug: str, title: str, body: str) -> str:
    return f'<section id="{slug}">\n<h2>{html.escape(title)}</h2>\n{body}\n</section>'


def section_likes(groups: list[dict]) -> str:
    return "\n".join(
        f'<section id="likes-{i}">\n<h2>{html.escape(g["title"])}</h2>\n<p>{"、".join(html.escape(x) for x in g["items"])}</p>\n</section>'
        for i, g in enumerate(groups, start=1)
    )


def render_thumbs(post: dict) -> str:
    if not post["media"]:
        return ""
    thumbs = "".join(
        f'<button class="shot" type="button" data-post="{post["id"]}" data-index="{i}" aria-label="写真{i + 1}">'
        f'<img src="images/{m["file"]}" width="{m["w"]}" height="{m["h"]}" loading="lazy" decoding="async" alt=""></button>'
        for i, m in enumerate(post["media"])
    )
    return f'<div class="thumbs">{thumbs}</div>'


def render_post(post: dict, handle: str) -> str:
    url = f"https://x.com/{handle}/status/{post['id']}"
    text = html.escape(post["text"]).replace("\n", "<br>")
    return (
        f'<li><time datetime="{post["date"]}"><a href="{url}" target="_blank" rel="noopener">{format_date(post["date"])}</a></time>'
        f"<p>{text}</p>{render_thumbs(post)}</li>"
    )


def section_posts(posts: list[dict], handle: str) -> str:
    items = "\n".join(render_post(p, handle) for p in posts)
    return f'<p class="lead">X に書いたもののうち、読み返したい{len(posts)}件。日付を押すと元の投稿へ。</p>\n<ol class="posts">{items}</ol>'


def section_music(site: dict) -> str:
    name = html.escape(site["playlist_name"])
    return (
        f'<p><a href="https://open.spotify.com/playlist/{site["playlist_id"]}" target="_blank" rel="noopener">{name}</a>（Spotify）</p>'
        f'<iframe src="https://open.spotify.com/embed/playlist/{site["playlist_id"]}?theme=0" title="Spotify: {name}" loading="lazy" '
        'allow="clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>'
    )


def section_wishlist(site: dict) -> str:
    return f'<p><a href="{site["wishlist_url"]}" target="_blank" rel="noopener">Amazon のほしい物リスト</a></p>'


def main() -> None:
    site = read_json("site.json")
    posts = read_json("posts.json")
    posts.sort(key=lambda p: p["date"], reverse=True)

    body = "\n".join(
        [
            section_likes(site["likes"]),
            section("posts", "旅の投稿", section_posts(posts, site["handle"])),
            section("music", "音楽", section_music(site)),
            section("wishlist", "ほしいもの", section_wishlist(site)),
        ]
    )
    toc_items = [(f"likes-{i}", g["title"]) for i, g in enumerate(site["likes"], start=1)] + [
        ("posts", "旅の投稿"),
        ("music", "音楽"),
        ("wishlist", "ほしいもの"),
    ]
    toc = "｜".join(f'<a href="#{slug}">{html.escape(title)}</a>' for slug, title in toc_items)

    lightbox_data = json.dumps(
        {p["id"]: [{"src": f"images/{m['file']}", "w": m["w"], "h": m["h"]} for m in p["media"]] for p in posts},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    output = (ROOT / "template.html").read_text(encoding="utf-8")
    for key, value in {
        "TITLE": site["title"],
        "DESCRIPTION": site["description"],
        "URL": site["url"],
        "OGP_IMAGE": site["ogp_image"],
        "HANDLE": site["handle"],
        "SINCE": format_date(site["since"]),
        "LEAD": site["lead"],
        "TOC": toc,
        "BODY": body,
        "LIGHTBOX_DATA": lightbox_data,
    }.items():
        output = output.replace("{{" + key + "}}", value)

    leftover = re.findall(r"{{[A-Z_]+}}", output)
    if leftover:
        raise SystemExit(f"未置換のプレースホルダ: {leftover}")

    (ROOT / "index.html").write_text(output, encoding="utf-8")
    print(f"index.html: {len(site['likes'])} lists, {len(posts)} posts")


if __name__ == "__main__":
    main()
