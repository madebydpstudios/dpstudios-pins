# Made by DP Studios: Pinterest pin feed

Approved Pinterest pins for the [Made by DP Studios Etsy shop](https://www.etsy.com/shop/MadebyDPStudiosUS), published as RSS so Zapier can post them to Pinterest automatically.

## How it works

1. Claude designs pins (`tools/render_pins.py`) and saves the images in `pins/`.
2. Each new pin waits for approval in the **DP Studios HQ** dashboard (Pins tab).
3. Approved pins are added to `data/published.json`, and `tools/build_feed.py` rebuilds the feeds.
4. GitHub Pages serves the feeds. Zapier (RSS → Pinterest "Create Pin") posts each new item.

## Feeds

- All pins: https://madebydpstudios.github.io/dpstudios-pins/feeds/all.xml
- One feed per Pinterest board: `feeds/<board-name>.xml`

## Files

- `pins/` pin images (1000×1500 JPG)
- `data/published.json` approved, published pins (source for the feeds)
- `tools/render_pins.py` pin designer (brand spec v3)
- `tools/build_feed.py` feed builder
