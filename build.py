"""Pre-render every reel link and SEO tags. Python standard library only."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PATTERN = re.compile(r"^/(reel|reels|p)/([A-Za-z0-9_-]+)/?$")


def normalize(value):
    if not isinstance(value, str):
        raise ValueError("Every entry in videos.json must be a link string.")
    parsed = urlsplit(value.strip())
    match = PATTERN.fullmatch(parsed.path)
    if (parsed.scheme != "https" or parsed.netloc not in {"instagram.com", "www.instagram.com"}
            or not match):
        raise ValueError(f"Invalid Instagram reel/post link: {value!r}")
    kind, shortcode = match.groups()
    return f"https://www.instagram.com/{'reel' if kind == 'reels' else kind}/{shortcode}/", shortcode


def replace_region(document, name, content):
    return re.sub(rf"<!-- {name}:START -->.*?<!-- {name}:END -->",
                  lambda _: f"<!-- {name}:START -->\n{content}\n<!-- {name}:END -->",
                  document, flags=re.S)


def build(output, site_url=None):
    data = json.loads((ROOT / "videos.json").read_text())
    if not isinstance(data, list):
        raise ValueError("videos.json must be an array of link strings.")
    videos, seen = [], set()
    for value in data:
        url, shortcode = normalize(value)
        if shortcode not in seen:
            seen.add(shortcode)
            videos.append((url, shortcode))
    source = (ROOT / "index.html").read_text()
    template = re.search(r'<template id="reel-template">(.*?)</template>', source, re.S).group(1)
    articles = []
    for number, (url, shortcode) in enumerate(videos, 1):
        articles.append(template.replace("__URL__", html.escape(url, quote=True))
                        .replace("__ID__", shortcode).replace("__NUMBER__", str(number)))
    source = replace_region(source, "REELS", "\n".join(articles))
    directory = '\n'.join(f'<li><a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Instagram reel {number}</a></li>'
                          for number, (url, _) in enumerate(videos, 1))
    source = replace_region(source, "DIRECTORY", directory)
    if videos:
        source = source.replace('id="directory" hidden', 'id="directory"')
    source = source.replace('id="feed-count">Loading collection…',
                            f'id="feed-count">{len(videos)} reel{"s" if len(videos) != 1 else ""}')
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Loop — Instagram reel collection",
              "description": "A curated collection of Instagram reels.",
              "mainEntity": {"@type": "ItemList", "numberOfItems": len(videos), "itemListElement": [
                  {"@type": "ListItem", "position": number, "name": f"Instagram reel {number}", "url": url}
                  for number, (url, _) in enumerate(videos, 1)]}}
    tags = []
    if site_url:
        parsed = urlsplit(site_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment or parsed.username:
            raise ValueError("--site-url must be your public HTTPS site URL without query/fragment.")
        site_url = site_url.rstrip("/") + "/"
        schema["url"] = site_url
        safe_url = html.escape(site_url, quote=True)
        tags.extend([f'<link rel="canonical" href="{safe_url}">',
                     f'<meta property="og:url" content="{safe_url}">'])
    tags.append('<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>')
    source = replace_region(source, "SEO", "\n".join(tags))
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents and output.name in {".git", ".agents", ".codex", ".aws"}:
        raise ValueError("Use a separate output directory, such as dist.")
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(source)
    (output / "videos.json").write_text(json.dumps([url for url, _ in videos], indent=2) + "\n")
    (output / ".nojekyll").touch()
    if site_url:
        # Hash fragments do not represent independently indexable pages: sitemap the actual page only.
        (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{html.escape(site_url)}</loc></url></urlset>\n')
        (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}sitemap.xml\n")
    else:
        for filename in ("sitemap.xml", "robots.txt"):
            (output / filename).unlink(missing_ok=True)
    print(f"Built {len(videos)} reels in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "dist"))
    parser.add_argument("--site-url", help="Public GitHub Pages/custom domain URL, including repository path")
    args = parser.parse_args()
    build(args.out, args.site_url)
