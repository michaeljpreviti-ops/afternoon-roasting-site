"""Prepare image assets for the Afternoon Roasting site.

Reads the untouched originals in assets/img/src/ and writes the web-sized
copies the page actually loads. Re-runnable and idempotent: it never writes
back into src/.

    python3 -m pip install --user Pillow
    python3 src/prep_assets.py

Three jobs:
  * the daisy mark — the source PNG is drawn on an opaque white square, so the
    white is keyed out to alpha and the art is cropped to its own bounding box.
    A second copy sits on a white disc, for the dark theme where bare white
    petal outlines would disappear;
  * the bag shots and photos — resized to the longest edge the layout can use
    on a 2x screen, re-encoded as progressive JPEG;
  * the favicon/app icon — the daisy centred on brand blue.
"""
import pathlib
import sys

from PIL import Image

IMG = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img"
SRC = IMG / "src"

BLUE = (0, 86, 184)
YELLOW = (255, 206, 0)

# longest edge, quality — squares are the product grid, wides are the bands
SIZES = {
    "bags": (900, 72),
    "shop": (1400, 70),
    "roastery": (1400, 70),
}

# where each source file lands: (subfolder, output name)
PLACEMENT = {
    "bag-always.jpg": ("bags", "always.jpg"),
    "bag-decaf.jpg": ("bags", "decaf.jpg"),
    "bag-duromina.jpg": ("bags", "duromina.jpg"),
    "bag-kembata.jpg": ("bags", "kembata.jpg"),
    "bag-halfcaff.jpg": ("bags", "half-caff.jpg"),
    "bag-mexico.jpg": ("bags", "mexico.jpg"),
    "bag-growhub.jpg": ("bags", "grow-hub.jpg"),
    "tee-psycho.jpg": ("bags", "tee-psycho.jpg"),
    "shop-storefront.jpg": ("shop", "storefront.jpg"),
    "shop-daisy-latte.jpg": ("shop", "daisy-latte.jpg"),
    "shop-latte-pastry.jpg": ("shop", "latte-pastry.jpg"),
    "shop-farm-board.jpg": ("shop", "farm-board.jpg"),
    "shop-two-drinks.jpg": ("shop", "two-drinks.jpg"),
    "shop-patio-cups.jpg": ("shop", "patio-cups.jpg"),
    "shop-flag-dusk.jpg": ("shop", "flag-dusk.jpg"),
    "shop-flag-day.jpg": ("shop", "flag-day.jpg"),
    "shop-flowers.jpg": ("shop", "flowers.jpg"),
    "shop-menu-board.jpg": ("shop", "menu-board.jpg"),
    "shop-interior.jpg": ("shop", "interior.jpg"),
    "roastery-drum.jpg": ("roastery", "drum.jpg"),
    "roastery-pat.jpg": ("roastery", "pat.jpg"),
    "origin-oaxaca.jpg": ("roastery", "origin-oaxaca.jpg"),
    "growhub-entrance.jpg": ("roastery", "grow-hub.jpg"),
}

WHITE_CUT = 246  # anything at or above this in all channels is the paper plate


def key_out_white(path):
    """White-plate artwork -> the same art with an alpha channel, cropped."""
    im = Image.open(path).convert("RGB")
    px = im.load()
    alpha = Image.new("L", im.size, 0)
    ap = alpha.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b = px[x, y]
            # distance from white, scaled so near-white edges stay soft
            d = 255 - min(r, g, b)
            ap[x, y] = 0 if min(r, g, b) >= WHITE_CUT else min(255, d * 4)
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop(alpha.getbbox())


def on_disc(mark, pad_ratio=0.14):
    """The mark centred on an opaque white disc, for dark backgrounds."""
    side = int(max(mark.size) * (1 + pad_ratio * 2))
    disc = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ring = Image.new("L", (side * 4, side * 4), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(ring).ellipse((0, 0, side * 4 - 1, side * 4 - 1), fill=255)
    ring = ring.resize((side, side), Image.LANCZOS)
    plate = Image.new("RGBA", (side, side), (255, 255, 255, 255))
    plate.putalpha(ring)
    plate.alpha_composite(
        mark, ((side - mark.size[0]) // 2, (side - mark.size[1]) // 2))
    return plate


def fit(path, out, longest, quality):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    scale = longest / max(w, h)
    if scale < 1:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC} — the untouched originals live there")

    mark = key_out_white(SRC / "daisy-src.png")
    mark.resize((512, round(512 * mark.size[1] / mark.size[0])),
                Image.LANCZOS).save(IMG / "daisy.png")
    disc = on_disc(mark)
    disc.resize((512, 512), Image.LANCZOS).save(IMG / "daisy-disc.png")

    # The petals are outline-only, so the icon uses the disc version: bare
    # petals on brand blue would read as a yellow dot with nothing around it.
    icon = Image.new("RGBA", (max(disc.size) + 150,) * 2, BLUE + (255,))
    icon.alpha_composite(disc, ((icon.size[0] - disc.size[0]) // 2,
                                (icon.size[1] - disc.size[1]) // 2))
    icon.resize((512, 512), Image.LANCZOS).save(IMG / "icon-512.png")
    print(f"daisy.png {mark.size} -> 512 wide, daisy-disc.png, icon-512.png")

    for name, (folder, out_name) in sorted(PLACEMENT.items()):
        src = SRC / name
        if not src.exists():
            print(f"  skip {name} (not in src/)")
            continue
        longest, quality = SIZES[folder]
        key = f"{folder}/{out_name}"
        size = fit(src, IMG / folder / out_name, longest, quality)
        print(f"  {key} {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
