# Afternoon Roasting — site

A rebuilt single-page site for **Afternoon Roasting / Afternoon Coffee**, 619 S Main St Unit 5,
Gainesville FL. Small-batch coffee roaster and coffeeshop. Roasts Mondays, ships Tuesdays; the
cafe is open daily 7:30 AM – 3 PM.

This replaces the look of the current Shopify storefront at <https://afternoonroasting.com>.
It does **not** replace the store — every Buy button links straight back to the existing
Shopify product page, so checkout, inventory and the Coffee Club subscription stay where they
already work.

## Build

```sh
python3 -m pip install --user Pillow   # once, for src/prep_assets.py only
python3 src/gen.py                     # writes index.html and artifact.html
```

`src/gen.py` is the only thing to edit — **never hand-edit `index.html` or `artifact.html`**,
they are generated. The content blocks at the top of `gen.py` hold everything that changes:
`BUSINESS`, `COFFEES`, `CLUB`, `MERCH`, `BOARD`, `STEPS`, `FAQ`, `REVIEWS` and the photo lists.
`src/_css.css` is the stylesheet and `src/_app.js` the behaviour; both are inlined at build time
so the page is one request.

Two outputs from one body of markup:

| file | what it is |
| --- | --- |
| `index.html` | standalone page with `<head>`, meta tags and schema.org markup — this is what gets deployed |
| `artifact.html` | the same page as a body fragment, for publishing through the Artifact tool |

`src/prep_assets.py` regenerates everything in `assets/img/` from the untouched originals in
`assets/img/src/`. It only needs re-running when a source image changes. It keys the white plate
out of the daisy mark, puts a copy on a white disc (so one file reads on both themes), builds the
favicon, and resizes the photos. `assets/img/daisy.png` — the bare transparent mark — is written
for reuse but the page itself does not load it.

## What's on the page

Sticky header with a live Google rating chip · hero with an open/closed clock in the cafe's own
time zone · the seven-coffee shelf with cupping notes, farm data and prices by size · Coffee Club
· the roasting week, Monday to Wednesday · the cafe board · twelve Google reviews in an
auto-advancing carousel · photo gallery · merch · FAQ accordion · visit details · footer ·
accessibility toolbar · light and dark themes · schema.org `CafeOrCoffeeShop` and `FAQPage`.

## Accessibility

Target is **WCAG 2.1 AA**.

- `gen.py` **fails the build** if any colour pair drops below its minimum — body text and accents
  at 4.5:1, control borders at 3:1 — checked in both themes and again against the hero's tinted
  plate. `--line-strong` is for control borders (WCAG 1.4.11); `--line` is for decorative
  dividers, which have no minimum. All 51 pairs pass as of this commit.
- Still to do: a pass with **axe-core** and one with the **WAVE** Chrome extension against the
  deployed URL. Claude cannot click extension toolbar icons, so WAVE is manual.

The bottom-left toolbar is the same component as the Dave Barber's and Brew & Root sites, in
Afternoon's blue: font size and line height steppers, readable font, letter spacing, text align,
font weight, big cursor; light / high / monochrome contrast; reading line, reading mask, hide
images, highlight content, stop animations, highlight links; and Reset Settings. Close it with
the X, the Hide Toolbar link, or Escape.

Two rules keep it safe to bolt on, and both must survive any edit:

1. everything it draws carries `.a11y-ui`, and every page-wide override is scoped to
   `body > *:not(.a11y-ui)`, so the panel can never restyle its own controls;
2. the panel sizes itself in **px, never rem**, so the Font Size control cannot shrink the buttons
   someone needs in order to undo it.

Choices persist per-device in `localStorage`, wrapped in try/catch so a private window or blocked
storage degrades quietly. The panel keeps its own fixed light palette, checked by `PANEL_PAIRS`.

The review carousel auto-advances with a visible Pause control (WCAG 2.2.2), holds while the
pointer or keyboard focus is inside it, and does not move at all under `prefers-reduced-motion`.

## Where the content came from

Everything on the page is the business's own material. Nothing is invented.

- **Coffee, prices, sizes, cupping notes, farm data and stock** — the shop's own Shopify product
  feed and product pages, read 2026-10-30. All seven coffees were in stock; the Sade Tee was sold
  out, so it is not on the page.
- **Shipping, pickup, local delivery and wholesale** — the shop's own FAQ page, verbatim in
  substance.
- **Hours, address, rating and reviews** — the Afternoon Coffee Google Business listing, read
  2026-10-30: 4.6 from 80 reviews, open daily 7:30 AM – 3 PM, `$1–10`, dine-in / takeout /
  delivery. The twelve reviews are real five-star ones, lightly trimmed for length and normalised
  for capitalisation.
- **Email** — `afternoonroasting@gmail.com`, from the shop's own accessibility statement.
- **Photos** — bag artwork and the roastery and origin shots are the shop's own product images
  from its Shopify CDN. The shop photos (storefront, interior, drinks, flowers, menu board, farm
  board, COFFEE flag) are the **owner-uploaded** photos on the Google listing. No customer review
  photos are used.
- **Brand colours** — `#0056B8` and `#FFCE00`, sampled straight out of the daisy logo PNG.
- **Type** — Jost stands in for the Futura the shop letters its board and its bags in; Atkinson
  Hyperlegible carries the body copy.

## Open questions for the owner

Worth asking before this goes anywhere near the live domain:

1. **No phone number anywhere.** The Google listing shows "Add place's phone number" and the site
   has none. Is there one to publish, or is email deliberate?
2. **The cafe board photo is from June 2025.** Prices on the page (Americano $3, latte $5, mocha
   $6, matcha latte $6, cold brew $5, syrups $1) are transcribed from it. Are they still current?
   Is there anything on the board now that isn't listed — the affogato and the sparkling mango
   matcha both come up in reviews but aren't painted up.
3. **Decaf Colombia pricing looks off.** 300 g is $18 but 1 lb is $22, while every other coffee
   jumps from $18–20 at 300 g to $52–60 at 2.5 lb. Is the 1 lb price right?
4. **Grow Hub Dark Roast** says $1 a bag goes to Grow Hub. Still true? Should the page link to
   growhub.org?
5. **Swallowtail Farm.** Reviews and the shop's own chalkboard say the beef, dairy and flowers are
   Swallowtail's, and one review calls the shop a collaboration with them. Is that a partnership
   worth naming on the page, with a link?
6. **Online ordering.** The Google listing has an "Order online" button for the cafe. If there is
   a Toast/Square/Owner ordering link, it belongs in the header next to Shop coffee.
7. **Facebook.** The site links only Instagram (`@afternoon__coffee`). Is there a Facebook page?
8. **The Psycho Killer tee** is the only merch in stock. Keep it on the page, or drop merch until
   there is more?

## Deploy

Static, no build step on the host. `vercel.json` sets `cleanUrls`, a one-year immutable cache on
`/assets/*`, and `nosniff` / `strict-origin-when-cross-origin` headers.
