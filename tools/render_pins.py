"""Render Pinterest pins (1000x1500, v3 brand spec) from a JSON spec.

Usage: python tools/render_pins.py specs.json out_dir
Each spec: {id, eyebrow, headline, sub, card_title, tiles:[[label,value],[label,value]],
            rows:[[name, pill_text, pill_color]], seal, badges:[...], price, compare}
pill_color: g (green) | y (gold) | r (red) | x (gray)
"""
import html, json, pathlib, sys
from playwright.sync_api import sync_playwright

e = html.escape
CSS = """
*{box-sizing:border-box;margin:0}
body{width:1000px;height:1500px;overflow:hidden;font-family:Inter,'DejaVu Sans',sans-serif;color:#fff;
 background:linear-gradient(165deg,#1F3864 0%,#152A4D 55%,#0F1F3A 100%);display:flex;flex-direction:column;position:relative}
.g1{position:absolute;width:560px;height:560px;right:-180px;top:-180px;border-radius:50%;background:radial-gradient(circle,rgba(47,191,159,.3),transparent 65%)}
.g2{position:absolute;width:560px;height:560px;left:-220px;bottom:-160px;border-radius:50%;background:radial-gradient(circle,rgba(245,166,35,.22),transparent 65%)}
.in{padding:44px 48px 0;position:relative;display:flex;flex-direction:column;zoom:1.25}
.logo{display:flex;align-items:center;gap:12px}
.mk{display:grid;grid-template-columns:18px 18px;gap:4px}.mk i{width:18px;height:18px;border-radius:5px;background:#2FBF9F;display:block}
.mk i:first-child{background:#fff}.mk i:last-child{background:#F5A623}
.wm{font:600 24px Inter}.wm b{color:#F5A623;font-weight:800}
.eb{margin-top:40px;font:700 20px Inter;letter-spacing:.14em;text-transform:uppercase;color:#2FBF9F}
h1{margin-top:14px;font:800 54px/1.08 'Inter Display',Inter;letter-spacing:-.015em}
.sub{margin-top:16px;font:500 24px/1.4 Inter;color:#C9D4EA}
.card{margin-top:40px;background:#fff;color:#16213A;border-radius:22px;box-shadow:0 26px 60px rgba(0,0,0,.35);position:relative}
.ch{background:#1F3864;color:#fff;border-radius:22px 22px 0 0;padding:20px 28px;padding-right:160px;font:700 24px Inter}
.cb{padding:24px 28px}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:10px}
.tile{border-radius:14px;padding:16px 18px;background:#E8F7F3}.tile:nth-child(2){background:#FDE9E0}
.tile .l{font:700 15px Inter;color:#5B6782;text-transform:uppercase;letter-spacing:.05em}
.tile .v{font:800 38px Inter;color:#1F3864;margin-top:4px}
.row{display:flex;justify-content:space-between;align-items:center;padding:15px 4px;border-bottom:2px solid #EEF1F6;font:600 24px Inter}
.row:last-child{border:0}
.pill{padding:6px 16px;border-radius:99px;font:700 17px Inter;white-space:nowrap}
.g{background:#C6E0B4;color:#2E5A22}.y{background:#FFE699;color:#7A5C00}.r{background:#F8CBAD;color:#8A2E16}.x{background:#E0E0E0;color:#444}
.seal{position:absolute;right:-26px;top:-62px;width:132px;height:132px;border-radius:50%;background:#F5A623;border:4px solid #fff;transform:rotate(-10deg);
 display:flex;align-items:center;justify-content:center;text-align:center;font:900 13px/1.15 Inter;color:#1B1300;padding:14px;box-shadow:0 10px 22px rgba(0,0,0,.35)}
.badges{display:flex;gap:10px;margin-top:26px;flex-wrap:wrap}
.badge{background:rgba(255,255,255,.12);border:1.5px solid rgba(255,255,255,.25);border-radius:99px;padding:9px 18px;font:600 18px Inter}
.bar{margin-top:auto;background:rgba(0,0,0,.3);padding:24px 60px;display:flex;justify-content:space-between;align-items:center;position:relative}
.price{font:800 40px Inter}.price s{font:500 24px Inter;color:#9AA7C2;margin-left:10px}
.btn{background:#F5A623;color:#1B1300;font:800 24px Inter;padding:16px 28px;border-radius:12px}
.wmk{background:#0B1630;padding:10px 60px;text-align:right;font:500 16px Inter;color:#8FA0C2;position:relative}
"""

def page(s):
    tiles = "".join(f'<div class="tile"><div class="l">{e(l)}</div><div class="v">{e(v)}</div></div>' for l, v in s.get("tiles", []))
    rows = "".join(f'<div class="row"><span>{e(n)}</span><span class="pill {c}">{e(p)}</span></div>' for n, p, c in s["rows"])
    badges = "".join(f'<span class="badge">{e(b)}</span>' for b in s["badges"])
    comp = f'<s>{e(s["compare"])}</s>' if s.get("compare") else ""
    return f"""<!doctype html><html><head><style>{CSS}</style></head><body><div class="g1"></div><div class="g2"></div>
<div class="in"><div class="logo"><div class="mk"><i></i><i></i><i></i><i></i></div><div class="wm">Made by <b>DP</b> Studios</div></div>
<div class="eb">{e(s['eyebrow'])}</div><h1>{e(s['headline'])}</h1><div class="sub">{e(s['sub'])}</div>
<div class="card"><div class="seal">{s['seal']}</div><div class="ch">{e(s['card_title'])}</div><div class="cb">{('<div class="tiles">'+tiles+'</div>') if tiles else ''}{rows}</div></div>
<div class="badges">{badges}</div></div>
<div class="bar"><div class="price">{e(s['price'])}{comp}</div><div class="btn">Shop Now on Etsy →</div></div>
<div class="wmk">Etsy shop: MadebyDPStudiosUS</div></body></html>"""

if __name__ == "__main__":
    specs = json.load(open(sys.argv[1]))
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1000, "height": 1500})
        for s in specs:
            pg.set_content(page(s)); pg.wait_for_timeout(120)
            pg.screenshot(path=str(out / f"{s['id']}.jpg"), type="jpeg", quality=88)
            print(s["id"])
        b.close()
