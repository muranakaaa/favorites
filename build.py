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


def platform(number: int, slug: str, title: str, note: str, body: str) -> str:
    note_html = f'<span class="note">{html.escape(note)}</span>' if note else ""
    return f"""<section class="platform" id="{slug}">
<h2><span class="num">{number}</span><span class="name">{html.escape(title)}</span>{note_html}</h2>
{body}
</section>"""


def media_class(count: int) -> str:
    return {1: "m1", 2: "m2", 3: "m3"}.get(count, "m4")


def render_media(post: dict) -> str:
    if not post["media"]:
        return ""
    items = []
    for index, m in enumerate(post["media"]):
        items.append(
            f'<button class="shot" type="button" data-post="{post["id"]}" data-index="{index}">'
            f'<img src="images/{m["file"]}" width="{m["w"]}" height="{m["h"]}"'
            f' loading="lazy" decoding="async" alt=""></button>'
        )
    return f'<div class="media {media_class(len(items))}">{"".join(items)}</div>'


def render_post(post: dict, handle: str) -> str:
    url = f"https://x.com/{handle}/status/{post['id']}"
    text = html.escape(post["text"]).replace("\n", "<br>")
    return f"""<article class="post">
<p class="text">{text}</p>
{render_media(post)}
<footer class="meta"><time datetime="{post["date"]}">{format_date(post["date"])}</time>
<a href="{url}" target="_blank" rel="noopener">Xで見る</a></footer>
</article>"""


def section_about(site: dict) -> str:
    intro = "".join(f"<p>{html.escape(line)}</p>" for line in site["intro"])
    interests = "".join(f"<li>{html.escape(w)}</li>" for w in site["interests"])
    return (
        f'{intro}<p class="wip">{html.escape(site["intro_wip"])}</p>'
        f'<p><a href="https://x.com/{site["handle"]}" target="_blank" rel="noopener">X: @{site["handle"]}</a></p>'
        f'<h3>興味関心</h3><ul class="tags">{interests}</ul>'
    )


def section_posts(posts: list[dict], handle: str) -> str:
    feed = "\n".join(render_post(p, handle) for p in posts)
    return f'<div class="posts">{feed}</div>'


def section_music(site: dict) -> str:
    name = html.escape(site["playlist_name"])
    return (
        f'<iframe src="https://open.spotify.com/embed/playlist/{site["playlist_id"]}?theme=0" '
        f'title="Spotify: {name}" loading="lazy" '
        'allow="clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>'
        f'<p class="small"><a href="https://open.spotify.com/playlist/{site["playlist_id"]}" target="_blank" rel="noopener">'
        f"{name}</a> を Spotify で開く</p>"
    )


def section_wishlist(site: dict) -> str:
    return f'<p><a class="button" href="{site["wishlist_url"]}" target="_blank" rel="noopener">Amazon のほしい物リストを開く</a></p>'


def main() -> None:
    site = read_json("site.json")
    posts = read_json("posts.json")
    posts.sort(key=lambda p: p["date"], reverse=True)

    platforms = [
        ("about", "自己紹介", "", section_about(site)),
        ("posts", "旅の投稿", f"{len(posts)}件", section_posts(posts, site["handle"])),
        ("music", "音楽", site["playlist_name"], section_music(site)),
        ("wishlist", "ほしいもの", "", section_wishlist(site)),
    ]

    toc = "".join(
        f'<li><a href="#{slug}"><span class="num">{i}</span>{html.escape(title)}</a>'
        f'{f"<span class=note>{html.escape(note)}</span>" if note else ""}</li>'
        for i, (slug, title, note, _) in enumerate(platforms, start=1)
    )
    sections = "\n".join(platform(i, slug, title, note, body) for i, (slug, title, note, body) in enumerate(platforms, start=1))

    lightbox_data = json.dumps(
        {p["id"]: [{"src": f"images/{m['file']}", "w": m["w"], "h": m["h"]} for m in p["media"]] for p in posts},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    station = site["station"]
    output = (ROOT / "template.html").read_text(encoding="utf-8")
    for key, value in {
        "TITLE": site["title"],
        "DESCRIPTION": site["description"],
        "URL": site["url"],
        "OGP_IMAGE": site["ogp_image"],
        "HANDLE": site["handle"],
        "SINCE": format_date(site["since"]),
        "NOTICE": site["notice"],
        "STATION_KANA": station["kana"],
        "STATION_KANJI": station["kanji"],
        "STATION_ROMAJI": station["romaji"],
        "PREV_KANA": station["prev_kana"],
        "PREV_ROMAJI": station["prev_romaji"],
        "NEXT_KANA": station["next_kana"],
        "NEXT_ROMAJI": station["next_romaji"],
        "ADDRESS": station["address"],
        "TOC": toc,
        "SECTIONS": sections,
        "LIGHTBOX_DATA": lightbox_data,
    }.items():
        output = output.replace("{{" + key + "}}", value)

    leftover = re.findall(r"{{[A-Z_]+}}", output)
    if leftover:
        raise SystemExit(f"未置換のプレースホルダ: {leftover}")

    (ROOT / "index.html").write_text(output, encoding="utf-8")
    print(f"index.html: {len(platforms)} platforms, {len(posts)} posts")


if __name__ == "__main__":
    main()
