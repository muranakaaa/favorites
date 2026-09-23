"""data/ と images/ から index.html と posts.html を生成する。"""

import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
POSTS_PAGE = "posts.html"
POSTS_TITLE = "好きな自分のポスト"


def read_json(name: str) -> dict | list:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def format_date(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{year}.{int(month):02d}.{int(day):02d}"


def block(title: str, body: str) -> str:
    return f"<h3>{html.escape(title)}</h3>\n{body}"


def likes(groups: list[dict]) -> str:
    return "\n".join(block(g["title"], f'<p>{"、".join(html.escape(x) for x in g["items"])}</p>') for g in groups)


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
        f'<li><h3><a href="{url}" target="_blank" rel="noopener">{format_date(post["date"])}</a></h3>'
        f"<p>{text}</p>{render_thumbs(post)}</li>"
    )


def music(site: dict) -> str:
    name = html.escape(site["playlist_name"])
    return (
        f'<p><a href="https://open.spotify.com/playlist/{site["playlist_id"]}" target="_blank" rel="noopener">{name}</a>（Spotify）</p>'
        f'<iframe src="https://open.spotify.com/embed/playlist/{site["playlist_id"]}?theme=0" title="Spotify: {name}" loading="lazy" '
        'allow="clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>'
    )


def lightbox_data(posts: list[dict]) -> str:
    return json.dumps(
        {p["id"]: [{"src": f"images/{m['file']}", "w": m["w"], "h": m["h"]} for m in p["media"]] for p in posts},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def nav(site: dict, current: str) -> str:
    pages = [("", site["title"]), (POSTS_PAGE, POSTS_TITLE)]
    return "".join(
        f'<li{" class=current" if page == current else ""}><a href="./{page}">{html.escape(label)}</a></li>' for page, label in pages
    )


def render_page(site: dict, template: str, values: dict[str, str]) -> str:
    output = template
    for key, value in {
        "DESCRIPTION": site["description"],
        "URL": site["url"],
        "OGP_IMAGE": site["ogp_image"],
        "HANDLE": site["handle"],
        **values,
    }.items():
        output = output.replace("{{" + key + "}}", value)
    leftover = re.findall(r"{{[A-Z_]+}}", output)
    if leftover:
        raise SystemExit(f"未置換のプレースホルダ: {leftover}")
    return output


def main() -> None:
    site = read_json("site.json")
    posts = read_json("posts.json")
    posts.sort(key=lambda p: p["date"], reverse=True)
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    updated = datetime.date.today().strftime("%Y.%m.%d")

    top_body = "\n".join(
        [
            f'<p>{html.escape(site["lead"])}</p>',
            likes(site["likes"]),
            block(POSTS_TITLE, f'<p><a href="{POSTS_PAGE}">{len(posts)}件</a></p>'),
            block("音楽", music(site)),
            block("ほしいもの", f'<p><a href="{site["wishlist_url"]}" target="_blank" rel="noopener">Amazon のほしい物リスト</a></p>'),
            block("X", f'<p><a href="https://x.com/{site["handle"]}" target="_blank" rel="noopener">@{site["handle"]}</a></p>'),
        ]
    )
    index = render_page(
        site,
        template,
        {
            "TITLE": site["title"],
            "PAGE": "",
            "PAGE_HREF": "./",
            "H1": site["title"],
            "UPDATED": f'<p class="updated">最終更新 {updated}</p>',
            "NAV": nav(site, ""),
            "BODY": top_body,
            "LIGHTBOX_DATA": "{}",
        },
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    posts_body = (
        f"<p>X に書いたもののうち、読み返したい{len(posts)}件。日付を押すと元の投稿へ、写真を押すと大きく。</p>"
        f'<ul class="posts">{"".join(render_post(p, site["handle"]) for p in posts)}</ul>'
    )
    posts_page = render_page(
        site,
        template,
        {
            "TITLE": f"{POSTS_TITLE}｜{site['title']}",
            "PAGE": POSTS_PAGE,
            "PAGE_HREF": POSTS_PAGE,
            "H1": POSTS_TITLE,
            "UPDATED": "",
            "NAV": nav(site, POSTS_PAGE),
            "BODY": posts_body,
            "LIGHTBOX_DATA": lightbox_data(posts),
        },
    )
    (ROOT / POSTS_PAGE).write_text(posts_page, encoding="utf-8")
    print(f"index.html: {len(site['likes'])} lists / {POSTS_PAGE}: {len(posts)} posts / 最終更新 {updated}")


if __name__ == "__main__":
    main()
