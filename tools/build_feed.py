"""Build RSS feeds from data/published.json (approved pins only).

Writes feeds/all.xml plus one feed per Pinterest board (feeds/<board-slug>.xml).
Zapier's "RSS by Zapier → New Item in Feed" trigger watches a feed and
"Pinterest → Create Pin" posts each new item (image = enclosure URL).
"""
import json, os, pathlib, re
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://madebydpstudios.github.io/dpstudios-pins"
SHOP = "https://www.etsy.com/shop/MadebyDPStudiosUS"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def item(p):
    img = f"{BASE}/pins/{p['id']}.jpg"
    size = os.path.getsize(ROOT / "pins" / f"{p['id']}.jpg")
    when = datetime.fromisoformat(p["published_at"].replace("Z", "+00:00"))
    return f"""  <item>
    <title>{escape(p['title'])}</title>
    <link>{escape(p['link'])}</link>
    <guid isPermaLink="false">dpstudios-pin-{escape(p['id'])}</guid>
    <pubDate>{format_datetime(when)}</pubDate>
    <category>{escape(p['board'])}</category>
    <description>{escape(p['description'])}</description>
    <enclosure url="{img}" length="{size}" type="image/jpeg"/>
    <media:content url="{img}" medium="image" type="image/jpeg" width="1000" height="1500"/>
  </item>"""

def feed(title, path, pins):
    now = format_datetime(datetime.now(timezone.utc))
    body = "\n".join(item(p) for p in sorted(pins, key=lambda p: p["published_at"], reverse=True)[:50])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{escape(title)}</title>
  <link>{SHOP}</link>
  <atom:link href="{BASE}/{path}" rel="self" type="application/rss+xml"/>
  <description>Approved pins from Made by DP Studios</description>
  <language>en-us</language>
  <lastBuildDate>{now}</lastBuildDate>
{body}
</channel>
</rss>
"""
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(xml, encoding="utf-8")

if __name__ == "__main__":
    pins = json.loads((ROOT / "data" / "published.json").read_text())
    feed("Made by DP Studios: all pins", "feeds/all.xml", pins)
    boards = sorted({p["board"] for p in pins})
    for b in boards:
        feed(f"Made by DP Studios: {b}", f"feeds/{slug(b)}.xml", [p for p in pins if p["board"] == b])
    print(f"{len(pins)} published pins; feeds: all + {', '.join(slug(b) for b in boards) or 'none'}")
