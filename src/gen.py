#!/usr/bin/env python3
"""Build the Afternoon Roasting site.

Writes two files from one body of markup:
  index.html     a standalone page, ready to deploy
  artifact.html  the same page as a body fragment for the Artifact tool

Everything that can change — business facts, the coffee lineup, the cafe
board, reviews, photo captions — lives in the data blocks below. The CSS is
src/_css.css and the behaviour is src/_app.js; both are inlined at build time
so the page is a single request. Never hand-edit the generated HTML.

    python3 src/gen.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

SHOP = "https://afternoonroasting.com"

# --------------------------------------------------------------------------
# Business facts. Sources: afternoonroasting.com (its pages and its Shopify
# product feed) and the Afternoon Coffee Google Business listing, read
# 2026-10-30. The roastery has no published phone number.
# --------------------------------------------------------------------------
BUSINESS = {
    "name": "Afternoon Roasting",
    "short": "Afternoon",
    "cafe_name": "Afternoon Coffee",
    "tagline": "Roasted Monday",
    "street": "619 S Main St, Unit 5",
    "city": "Gainesville",
    "state": "FL",
    "zip": "32601",
    "email": "afternoonroasting@gmail.com",
    "open_hour": 7.5,        # 7:30 AM
    "close_hour": 15.0,      # 3 PM
    "hours_text": "Open daily, 7:30 AM – 3 PM",
    "open_label": "Open now · until 3 PM",
    "closed_label": "Closed · opens 7:30 AM",
    "instagram": "https://www.instagram.com/afternoon__coffee/",
    "instagram_handle": "@afternoon__coffee",
    "google_reviews": "https://www.google.com/maps/place/?q=place_id:ChIJIfI8S2uj6IgRZp7PWG9bGO8",
    "maps": "https://www.google.com/maps/dir/?api=1&destination=619+S+Main+St+Unit+5,+Gainesville,+FL+32601",
    "google_rating": 4.6,
    "google_count": 80,
    "price_band": "$1–10",
}

# --------------------------------------------------------------------------
# The coffee. Prices, sizes, cupping notes and farm data are lifted from the
# shop's own product pages; "buy" is the handle on afternoonroasting.com.
# --------------------------------------------------------------------------
COFFEES = [
    {
        "name": "Always Blend",
        "kind": "Signature blend",
        "profile": "Chocolate · Dark fruit · Juicy",
        "buy": "always-blend",
        "img": "always.jpg",
        "alt": "The Always Blend bag, a cream pouch with a red Always sticker, "
               "on a bright yellow ground.",
        "note": "The house blend, and the one pulled as espresso at the cafe. "
                "Rich, sweet and balanced, with a heavy body and a long "
                "finish. Makes an excellent cup of drip coffee too.",
        "facts": [("Coffees", "Colombia, Costa Rica, Ethiopia"),
                  ("Processing", "Washed &amp; natural")],
        "prices": [("300 g", "$18"), ("2.5 lb", "$52"), ("5 lb", "$104")],
    },
    {
        "name": "Ethiopia Duromina Organic",
        "kind": "Single origin · Floral",
        "profile": "Honey · Candied citrus",
        "buy": "ethiopia-duromina",
        "img": "duromina.jpg",
        "alt": "The Ethiopia Duromina bag, printed with a wildflower drawing, "
               "on a pale blue ground.",
        "note": "A washed Agaro coffee from Red Fox Coffee Merchants, roasted "
                "light-medium to keep the florals on top.",
        "facts": [("Region", "Agaro"), ("Variety", "Ethiopia landraces"),
                  ("Processing", "Washed"), ("Altitude", "1,850–2,000 masl"),
                  ("Roast", "Light-medium")],
        "prices": [("300 g", "$20"), ("2.5 lb", "$60"), ("5 lb", "$120")],
    },
    {
        "name": "Ethiopia Kembata Natural",
        "kind": "Single origin · Fruity",
        "profile": "Strawberry · Blackberry · Pomegranate",
        "buy": "ethiopia-kembata-natural-process",
        "img": "kembata.jpg",
        "alt": "The Ethiopia Kembata bag, printed with a strawberry, on a "
               "bright red ground.",
        "note": "Grown at 2,050 metres in the Durame village of Kembata and "
                "dried on the fruit. The loudest coffee on the shelf.",
        "facts": [("Region", "Kembata"), ("Variety", "Ethiopia heirloom"),
                  ("Processing", "Natural"), ("Altitude", "2,050 masl"),
                  ("Roast", "Light-medium")],
        "prices": [("300 g", "$20"), ("2.5 lb", "$60"), ("5 lb", "$120")],
    },
    {
        "name": "Mexico Oaxaca San Pedro Yosotatu",
        "kind": "Single origin · Mild",
        "profile": "Key lime · Toasted almond · Brown sugar",
        "buy": "mexico-oaxaca-copy",
        "img": "mexico.jpg",
        "alt": "The Mexico Oaxaca bag, printed with a small landscape drawing, "
               "on an orange ground.",
        "note": "From the community of San Pedro Yosotatu in Oaxaca, through "
                "Red Fox Coffee Merchants. An easy, sweet medium roast.",
        "facts": [("Region", "Oaxaca"), ("Variety", "Pluma, Bourbon, Typica"),
                  ("Processing", "Washed"), ("Altitude", "1,700–1,900 masl"),
                  ("Roast", "Medium")],
        "prices": [("300 g", "$19"), ("2.5 lb", "$58"), ("5 lb", "$115")],
    },
    {
        "name": "Grow Hub Dark Roast",
        "kind": "Collaboration · Dark",
        "profile": "Bittersweet chocolate · Toasted nuts",
        "buy": "grow-hub-dark-roast",
        "img": "grow-hub.jpg",
        "alt": "The Grow Hub Dark Roast bag, printed with a garden scene, on a "
               "turquoise ground.",
        "note": "A longer, hotter roast for sweetness and body &mdash; classic "
                "dark, never smoky. Made with Grow Hub, the Gainesville "
                "non-profit plant nursery that employs adults living with "
                "disabilities. $1 from every bag goes to them.",
        "facts": [("Coffees", "Central and South America"),
                  ("Processing", "Washed"), ("Roast", "Dark")],
        "prices": [("300 g", "$18"), ("2.5 lb", "$52"), ("5 lb", "$104")],
        "flag": "$1 a bag to Grow Hub",
    },
    {
        "name": "Half Caff",
        "kind": "Blend · Half decaf",
        "profile": "Graham cracker · Molasses",
        "buy": "half-caff",
        "img": "half-caff.jpg",
        "alt": "The Half Caff bag, printed with a green Half Caff stamp, on a "
               "pale blue ground.",
        "note": "For anyone who wants a second cup in the afternoon without "
                "paying for it at 11 PM.",
        "facts": [("Coffees", "Guatemala, Costa Rica, Colombia"),
                  ("Processing", "Washed, sugar cane decaffeination")],
        "prices": [("300 g", "$18"), ("2.5 lb", "$52"), ("5 lb", "$104")],
    },
    {
        "name": "Decaf Colombia Valle del Cauca",
        "kind": "Single origin · Decaf",
        "profile": "Milk chocolate · Walnut · Creamy",
        "buy": "decaf",
        "img": "decaf.jpg",
        "alt": "The Decaf Colombia bag, printed with a circular Decaf seal, on "
               "a pale pink ground.",
        "note": "Banana bread and chocolate, silky body, low acidity. "
                "Decaffeinated in Colombia with sugar-cane ethyl acetate, "
                "which takes out 97% of the caffeine and leaves the sugars "
                "alone.",
        "facts": [("Region", "Valle del Cauca"),
                  ("Variety", "Caturra, Castillo"),
                  ("Processing", "Washed &amp; EA decaffeination"),
                  ("Altitude", "1,750 masl")],
        "prices": [("300 g", "$18"), ("1 lb", "$22"), ("5 lb", "$110")],
    },
]

# The subscription, which does not fit the bag grid.
CLUB = {
    "buy": "coffee-subscription",
    "price": "From $18",
    "note": "A rotating selection at the lowest single-origin price, as often "
            "as you like &mdash; whatever is being loved at the moment. Pick "
            "the quantity, the frequency and the grind. Ships, or collect it "
            "at the roastery. Gifting is just the recipient's address in the "
            "shipping field.",
}

MERCH = {
    "name": "Psycho Killer Tee",
    "buy": "psycho-killer-afternoon-coffee",
    "price": "$30",
    "sizes": "S–XL",
    "img": "tee-psycho.jpg",
    "alt": "A black Psycho Killer tee held up against a pink wall, printed "
           "with a portrait and the Afternoon Coffee name.",
    "note": "Limited edition, garment-dyed cotton, printed in Gainesville.",
}

# --------------------------------------------------------------------------
# The cafe board at 619 S Main St, transcribed from the shop's own menu board.
# --------------------------------------------------------------------------
BOARD = [
    ("Espresso", [("Americano", "$3"), ("Shot", "$3"), ("Cappuccino", "$4"),
                  ("Cortado", "$4"), ("Latte", "$5"), ("Mocha", "$6")]),
    ("Coffee", [("Strong drip", "$2.50 / $3"), ("Cold brew", "$5")]),
    ("Matcha", [("Matcha latte", "$6")]),
    ("Syrups", [("Vanilla, caramel, lavender, chocolate", "$1")]),
]

# --------------------------------------------------------------------------
# How a bag gets from the roaster to a kitchen, from the shop's own FAQ.
# --------------------------------------------------------------------------
STEPS = [
    ("Monday", "Roasting day",
     "Everything goes through the drum in small batches. Every order is "
     "roasted the Monday before it leaves, not pulled off a shelf."),
    ("Tuesday", "Orders ship",
     "Out the door by USPS Priority 2-Day Express or UPS Ground Advantage, "
     "with tracking, so you can follow the bag."),
    ("Tuesday", "Or collect it",
     "Pickup at the roastery between 9 and 5. If that window does not work, "
     "say so and it gets worked out."),
    ("Wednesday", "Local delivery",
     "Free, within four miles of the roastery."),
]

FAQ = [
    ("Where does the coffee come from?",
     "Green coffee is sourced through three importers &mdash; Genuine Origin, "
     "Red Fox Coffee Merchants and Royal Coffee NYC &mdash; and roasted here "
     "in Gainesville."),
    ("I ordered coffee. When will it arrive?",
     "Roasting happens on Mondays and orders ship on Tuesdays, by USPS "
     "Priority 2-Day Express or UPS Ground Advantage. Tracking follows by "
     "email."),
    ("Can I pick my order up instead?",
     "Yes &mdash; at the roastery on Tuesdays between 9 and 5. If you cannot "
     "make that window, get in touch and it will be worked out."),
    ("Do you deliver locally?",
     "Free local delivery on Wednesdays, anywhere within four miles of the "
     "roastery."),
    ("I want to serve your coffee at my restaurant, cafe or bar.",
     "Wholesale is open. Email "
     f'<a href="mailto:{BUSINESS["email"]}">{BUSINESS["email"]}</a> and the '
     "conversation starts there."),
]

# --------------------------------------------------------------------------
# Reviews as posted publicly on the Afternoon Coffee Google listing, read
# 2026-10-30. Five-star reviews only, lightly trimmed for length.
# --------------------------------------------------------------------------
REVIEWS = [
    ("Zachary Bautista", "2 months ago",
     "Best coffee shop in Gainesville! Love coming by Afternoon Coffee to "
     "either pick up coffee, freshly roasted beans, or to sit and enjoy the "
     "garden outside. Great place to come get some work done, especially when "
     "the weather cools down."),
    ("YaoMing Li", "3 weeks ago",
     "I ordered an Iced Mocha and a Butter biscuit at this adorable spot. The "
     "coffee is high quality and really helped me get the second wind of the "
     "day. The staff were friendly and quick with the order."),
    ("Neal Winsomer", "2 months ago",
     "Enjoyed the sparkling mango matcha. Found the mix refreshing, balanced "
     "and delicious. Cute little spot with a crew that is on top of it and "
     "well engaged with each customer."),
    ("claudia arias", "9 months ago",
     "Great coffee and service. We go there every weekend and miss it when we "
     "are out of town. It is a short walk from Depot Park, which makes it very "
     "convenient. We love their affogato, cappuccino and iced latte."),
    ("Madison Harrison", "7 months ago",
     "Excellent, incredible, amazing! The espresso rocks. The tea is "
     "delicious. I love that they have local meats, dairy and flowers that "
     "makes them even cooler. And the outdoor area is so relaxing!"),
    ("Veritie Roueche", "6 months ago",
     "Every time I come in for coffee and sometimes a pastry or sandwich, the "
     "service is excellent, quick and friendly! The iced latte's slight foam "
     "from shaking to mix, instead of stirring, is genius and a true delight."),
    ("Jake Rose", "9 months ago",
     "Not only is the coffee superb &mdash; I got a perfectly crafted latte "
     "and loved it &mdash; but the place is very well maintained. Everything "
     "orderly and very clean. Highly recommend!"),
    ("Joshua Tracy", "a year ago",
     "Friendly staff, excellent coffee and great fresh farm products. Baked "
     "goods are excellent too. If you're familiar with Afternoon, then you "
     "know what to expect for coffee."),
    ("Caylee Weintraub", "a year ago",
     "I still have dreams of the matcha I got from here. The baristas are "
     "great, and the drinks are so good."),
    ("Dinah Ceilley", "7 months ago",
     "Lattes and matcha are among the best in Gainesville. Cute atmosphere and "
     "outdoor area as well."),
    ("Caitlyn M", "a year ago",
     "Atmosphere is so nice, the colour scheme and decor are beautiful. The "
     "drinks are amazing, we didn't get any pastries this time but they look "
     "good as well. We will be back for sure."),
    ("Travis", "a year ago",
     "Amazing coffee in a chill, welcoming shop. The baristas were friendly "
     "and hospitable which added to the enjoyable hang. Definitely a gem in "
     "the Gainesville coffee scene."),
]

# Photos of the shop itself, from the Afternoon Coffee Google listing.
# (file, alt, object-position) — several are portrait phone shots whose
# subject sits low, so the square crop needs telling where to look.
SHOP_PHOTOS = [
    ("daisy-latte.jpg",
     "A latte in an Afternoon Coffee Co. cup, its foam dusted through a daisy "
     "stencil in cocoa.", "50% 40%"),
    ("storefront.jpg",
     "The shopfront: a dark timber and glass unit under an awning, with "
     "planting along the walk.", "50% 50%"),
    ("flag-day.jpg",
     "A tall black feather flag reading COFFEE with an arrow, planted on the "
     "grass outside the white building.", "50% 50%"),
    ("interior.jpg",
     "Inside: a run of stools along a counter under a white pitched ceiling, "
     "with shelves of packaged goods.", "50% 55%"),
    ("two-drinks.jpg",
     "An iced matcha and a hot cup with a yellow lid, side by side on the "
     "counter.", "50% 50%"),
    ("patio-cups.jpg",
     "Two hands holding a cappuccino and a takeaway cup out on the patio, "
     "with the garden behind.", "50% 45%"),
    ("flowers.jpg",
     "A blue jug of fresh cut flowers on the counter beside the brew bar.",
     "50% 35%"),
    ("latte-pastry.jpg",
     "A takeaway latte and a pastry on a napkin at an outdoor table.",
     "50% 55%"),
]

ROASTERY_PHOTO = ("drum.jpg",
                  "Roasted coffee tumbling out of the drum into the cooling "
                  "tray, with the roaster watching the drop.")
ORIGIN_PHOTO = ("origin-oaxaca.jpg",
                "Two people stacking sacks of green coffee on a drying patio "
                "in Oaxaca.")
CAFE_PHOTO = ("menu-board.jpg",
              "The cafe's arched black menu board, listing espresso, coffee, "
              "matcha and syrups in white lettering.")
FARM_PHOTO = ("farm-board.jpg",
              "A chalkboard over the chest freezer listing Swallowtail Farm "
              "grassfed beef and dairy by the cut, with prices per pound.")

# --------------------------------------------------------------------------
# Palette. Every pair that carries text is checked against WCAG 2.1 AA below,
# and the build fails if one drops under. Blue and yellow are the daisy's own
# two colours, sampled from the mark: #0056B8 and #FFCE00.
# --------------------------------------------------------------------------
DARK = {
    "bg": "#0D1420", "surface": "#141D2C", "raised": "#1C2739",
    "fg": "#F3F6FA", "muted": "#A9B5C4", "line": "#28344A", "line-strong": "#7A8A9F",
    "accent": "#8CBBFF", "accent-ink": "#08121F", "glow": "#FFCE00",
}
LIGHT = {
    "bg": "#FBFAF5", "surface": "#FFFFFF", "raised": "#F1EFE4",
    "fg": "#16181D", "muted": "#4D525B", "line": "#DEDBCC", "line-strong": "#6B707A",
    "accent": "#0B51AE", "accent-ink": "#FFFFFF", "glow": "#7A5300",
}
# The accessibility toolbar keeps its own fixed light palette, in px and
# independent of the page theme, so that nothing it switches on can make its
# own controls unreadable. Checked like the rest.
PANEL = {
    "head": "#0B51AE", "head-hover": "#083E86", "head-fg": "#FFFFFF",
    "sub": "#D7E6FA", "bg": "#EEF1F5", "card": "#FFFFFF", "tile": "#F2F5F9",
    "tile-hover": "#E2EAF5", "tile-on": "#DCE8F8",
    "line": "#646C78", "ink": "#15181D", "soft": "#454C56",
}
PANEL_PAIRS = [
    ("head-fg", "head", 4.5, "panel title on the blue header"),
    ("sub", "head", 4.5, "panel subtitle on the blue header"),
    ("ink", "card", 4.5, "panel text on its cards"),
    ("ink", "tile", 4.5, "tile labels"),
    ("ink", "tile-hover", 4.5, "tile labels, hovered"),
    ("ink", "tile-on", 4.5, "tile labels, switched on"),
    ("ink", "bg", 4.5, "panel text on its ground"),
    ("soft", "bg", 4.5, "the storage note"),
    ("head-fg", "head-hover", 4.5, "hovered panel buttons"),
    ("line", "tile", 3.0, "tile borders"),
    ("line", "card", 3.0, "tile borders on cards"),
]

# (foreground, background, minimum ratio, what it is) for both palettes.
CONTRAST_PAIRS = [
    ("fg", "bg", 4.5, "body text"),
    ("fg", "surface", 4.5, "text on cards"),
    ("fg", "raised", 4.5, "text on raised panels"),
    ("muted", "bg", 4.5, "secondary text"),
    ("muted", "surface", 4.5, "secondary text on cards"),
    ("muted", "raised", 4.5, "secondary text on raised panels"),
    ("accent", "bg", 4.5, "links and accents"),
    ("accent", "surface", 4.5, "accents on cards"),
    ("accent", "raised", 4.5, "accents on raised panels"),
    ("accent-ink", "accent", 4.5, "text on accent buttons"),
    ("glow", "bg", 4.5, "star rating"),
    ("glow", "surface", 4.5, "star rating on cards"),
    ("glow", "raised", 4.5, "star rating on raised panels"),
    # WCAG 1.4.11: a control's own boundary needs 3:1. Plain dividers and card
    # edges are decorative, so --line is not held to it.
    ("line-strong", "bg", 3.0, "control borders"),
    ("line-strong", "surface", 3.0, "control borders on cards"),
    ("line-strong", "raised", 3.0, "control borders on panels"),
]

# Same checks against the hero plate, where the daisy glow tints the ground.
GLOW_PAIRS = [
    ("fg", "glow-bg", 4.5, "hero heading over the glow"),
    ("muted", "glow-bg", 4.5, "hero body text over the glow"),
    ("accent", "glow-bg", 4.5, "hero accents over the glow"),
    ("line-strong", "glow-bg", 3.0, "hero button borders over the glow"),
]

GLOW_ALPHA = 0.16  # peak opacity of the hero's radial glow


def _lum(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def blend(fg_hex, bg_hex, alpha):
    """Flatten a translucent colour over an opaque one."""
    f = [int(fg_hex[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg_hex[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(alpha * f[i] + (1 - alpha) * b[i]):02X}"
                         for i in range(3))


def check_contrast():
    """Fail the build if any text pair drops below its WCAG minimum."""
    problems = []
    for label, palette in (("dark", DARK), ("light", LIGHT)):
        # The hero sits on a tinted plate; check against its strongest point.
        palette = dict(palette)
        palette["glow-bg"] = blend(palette["glow"], palette["bg"], GLOW_ALPHA)
        for fg, bg, minimum, what in CONTRAST_PAIRS + GLOW_PAIRS:
            ratio = contrast(palette[fg], palette[bg])
            status = "ok " if ratio >= minimum else "FAIL"
            print(f"  {status} {label:5} {what:32} {palette[fg]} on {palette[bg]}"
                  f"  {ratio:5.2f}:1  (needs {minimum})")
            if ratio < minimum:
                problems.append(f"{label}: {what} is {ratio:.2f}:1, needs {minimum}:1")
    for fg, bg, minimum, what in PANEL_PAIRS:
        ratio = contrast(PANEL[fg], PANEL[bg])
        status = "ok " if ratio >= minimum else "FAIL"
        print(f"  {status} panel {what:32} {PANEL[fg]} on {PANEL[bg]}"
              f"  {ratio:5.2f}:1  (needs {minimum})")
        if ratio < minimum:
            problems.append(f"panel: {what} is {ratio:.2f}:1, needs {minimum}:1")
    if problems:
        raise SystemExit("Contrast check failed:\n  " + "\n  ".join(problems))


# --------------------------------------------------------------------------
# Small markup helpers
# --------------------------------------------------------------------------
def stars(rating, size=20):
    """Five stars with the rating's share filled, as one decorative SVG."""
    pid = f"starclip{str(rating).replace('.', '')}{size}"
    pct = max(0.0, min(1.0, rating / 5)) * 100
    path = ("M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.4-5.8-3-5.8 3 1.1-6.4"
            "-4.7-4.6 6.5-.9z")
    body = [f'<svg class="stars" width="{size * 5}" height="{size}" '
            f'viewBox="0 0 120 24" aria-hidden="true" focusable="false">',
            f'<defs><clipPath id="{pid}"><rect x="0" y="0" '
            f'width="{pct * 1.2:.2f}" height="24"></rect></clipPath></defs>']
    for i in range(5):
        body.append(f'<path d="{path}" transform="translate({i * 24} 0)" '
                    f'class="star star--empty"></path>')
    body.append(f'<g clip-path="url(#{pid})">')
    for i in range(5):
        body.append(f'<path d="{path}" transform="translate({i * 24} 0)" '
                    f'class="star star--full"></path>')
    body.append("</g></svg>")
    return "".join(body)


ICONS = {
    "instagram": ('<path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.43.43.7.83.91 1.4.17.42.37 1.04.42 2.2.06 1.3.07 1.7.07 4.9s0 3.6-.07 4.9c-.05 1.2-.25 1.8-.42 2.2a3.8 3.8 0 01-.9 1.4c-.44.43-.84.7-1.41.91-.42.17-1.04.37-2.2.42-1.3.06-1.7.07-4.9.07s-3.6 0-4.9-.07c-1.2-.05-1.8-.25-2.2-.42a3.8 3.8 0 01-1.4-.9 3.8 3.8 0 01-.91-1.41c-.17-.42-.37-1.04-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.05-1.2.25-1.8.42-2.2.22-.6.48-1 .9-1.4.43-.43.83-.7 1.4-.91.42-.17 1.04-.37 2.2-.42C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.8.07-1.1.05-1.7.24-2.1.4-.5.2-.9.44-1.3.84-.4.4-.64.8-.84 1.3-.16.4-.35 1-.4 2.1-.06 1.3-.07 1.7-.07 4.8s0 3.5.07 4.8c.05 1.1.24 1.7.4 2.1.2.5.44.9.84 1.3.4.4.8.64 1.3.84.4.16 1 .35 2.1.4 1.3.06 1.7.07 4.8.07s3.5 0 4.8-.07c1.1-.05 1.7-.24 2.1-.4.5-.2.9-.44 1.3-.84.4-.4.64-.8.84-1.3.16-.4.35-1 .4-2.1.06-1.3.07-1.7.07-4.8s0-3.5-.07-4.8c-.05-1.1-.24-1.7-.4-2.1-.2-.5-.44-.9-.84-1.3-.4-.4-.8-.64-1.3-.84-.4-.16-1-.35-2.1-.4C15.5 4 15.1 4 12 4z"></path>'
                  '<path d="M12 7a5 5 0 100 10 5 5 0 000-10zm0 8.25A3.25 3.25 0 1112 8.75a3.25 3.25 0 010 6.5z"></path>'
                  '<circle cx="17.25" cy="6.75" r="1.2"></circle>'),
    "pin": ('<path d="M12 2a7 7 0 00-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 00-7-7zm0 9.5A2.5 2.5 0 1112 6.5a2.5 2.5 0 010 5z"></path>'),
    "clock": ('<path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 110-16 8 8 0 010 16zm.5-13H11v6l5.2 3.1.8-1.3-4.5-2.7z"></path>'),
    "mail": ('<path d="M4 4h16a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm8 7.2L4.6 6.4 4 6v.6l8 5.2 8-5.2V6l-.6.4z"></path>'
             '<path d="M4 8.3V18h16V8.3l-8 5.2z"></path>'),
    "bag": ('<path d="M7 7V6a5 5 0 0110 0v1h3.1a1 1 0 011 1.1l-1.3 12a2 2 0 01-2 1.9H6.2a2 2 0 01-2-1.8l-1.3-12A1 1 0 013.9 7H7zm2 0h6V6a3 3 0 00-6 0v1z"></path>'),
    "truck": ('<path d="M2 6a1 1 0 011-1h10a1 1 0 011 1v2h2.6a2 2 0 011.7.94l1.4 2.3a2 2 0 01.3 1.05V16a1 1 0 01-1 1h-1.2a3 3 0 01-5.6 0H9.8a3 3 0 01-5.6 0H3a1 1 0 01-1-1V6zm12 4v3.6a3 3 0 012.9.4H20v-2.1L18.6 10H14zM7 15.5a1.4 1.4 0 102.8 0 1.4 1.4 0 00-2.8 0zm7.6 0a1.4 1.4 0 102.8 0 1.4 1.4 0 00-2.8 0z"></path>'),
    "access": ('<circle cx="12" cy="4.2" r="2.2"></circle>'
               '<path d="M19.1 8.1a1.1 1.1 0 00-1.32-.83L14.5 8a9.4 9.4 0 01-5 0L6.22 7.27A1.1 1.1 0 005.8 9.43l3.1.69v3.3l-1.9 6.2a1.15 1.15 0 002.2.68l1.86-5.7h1.88l1.86 5.7a1.15 1.15 0 002.2-.68l-1.9-6.2v-3.3l3.1-.69a1.1 1.1 0 00.9-1.33z"></path>'),
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" '
            f'focusable="false">{ICONS[name]}</svg>')


def tokens(palette):
    return "".join(f"--{k}:{v};" for k, v in palette.items())


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------
def wordmark(cls=""):
    """Daisy mark plus the name set in type. The mark ships on a white disc so
    it reads on the cream ground and on the dark theme without swapping art."""
    return (f'<span class="mark{cls}">'
            f'<img src="assets/img/daisy-disc.png" alt="" width="96" '
            f'height="96" decoding="async">'
            f'<span class="mark__txt"><b>afternoon</b><i>roasting</i></span>'
            f'</span>')


def star_badge(cls, size, extra=""):
    """The compact rating chip. Used in the header and again in the hero, so
    the rating is on screen before anyone scrolls."""
    b = BUSINESS
    return (f'<a class="{cls}" href="#reviews">{stars(b["google_rating"], size)}'
            f'<strong>{b["google_rating"]:.1f}</strong>{extra}'
            f'<span class="sr-only">out of 5, from {b["google_count"]} Google '
            f'reviews. Read the reviews.</span></a>')


def header():
    b = BUSINESS
    return f"""
<header class="hdr">
  <div class="wrap hdr__in">
    <a class="hdr__logo" href="#top">
      {wordmark()}<span class="sr-only">{b['name']} home</span>
    </a>
    {star_badge('navstars', 13, '<span class="navstars__n">Google</span>')}
    <nav class="nav" aria-label="Main">
      <a href="#coffee">Coffee</a>
      <a href="#cafe">Cafe</a>
      <a href="#reviews">Reviews</a>
      <a href="#visit">Visit</a>
    </nav>
    <a class="btn btn--ig" href="{b['instagram']}">
      {icon('instagram')}<span>{b['instagram_handle']}</span>
    </a>
    <a class="btn btn--solid" href="{SHOP}/collections/all">
      {icon('bag')}<span>Shop coffee</span>
    </a>
  </div>
</header>"""


def hero():
    b = BUSINESS
    big = (f'<img src="assets/img/shop/daisy-latte.jpg" '
           f'alt="{SHOP_PHOTOS[0][1]}" width="1054" height="1400" '
           f'loading="eager" decoding="async" '
           f'style="object-position:{SHOP_PHOTOS[0][2]}">')
    small = (f'<img src="assets/img/roastery/drum.jpg" alt="{ROASTERY_PHOTO[1]}" '
             f'width="1400" height="1400" loading="lazy" decoding="async">'
             f'<img src="assets/img/shop/flag-day.jpg" alt="{SHOP_PHOTOS[2][1]}" '
             f'width="1050" height="1400" loading="lazy" decoding="async">')
    return f"""
<section class="hero" id="top" aria-labelledby="hero-heading">
  <div class="wrap hero__in">
    <div>
      <p class="eyebrow">Gainesville, Florida &middot; since the shop on South Main</p>
      <h1 id="hero-heading">Roasted Monday.<br><em>Shipped Tuesday.</em></h1>
      <p class="hero__lede">A microscopic roaster and coffeeshop giving it our
        all to source, roast and serve the finest coffees. Seven bags on the
        shelf, an espresso bar at 619&nbsp;S&nbsp;Main, and coffee that reaches
        you days old rather than months.</p>
      <div class="hero__meta">
        {star_badge('herostars', 17,
                    f'<span class="herostars__n">{b["google_count"]} Google reviews</span>')}
        <p class="status" id="status" data-open="unknown">
          <span class="status__dot" aria-hidden="true"></span>
          <span class="status__text">{b['hours_text']}</span>
        </p>
      </div>
      <div class="hero__cta">
        <a class="btn btn--solid" href="#coffee">See the coffee</a>
        <a class="btn btn--ghost" href="#visit">Visit the cafe</a>
      </div>
    </div>
    <div class="hero__art">{big}{small}</div>
  </div>
</section>"""


def coffee():
    cards = []
    for c in COFFEES:
        facts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>"
                        for k, v in c["facts"])
        prices = "".join(
            f'<li><span class="bag__size">{size}</span>'
            f'<span class="bag__price">{price}</span></li>'
            for size, price in c["prices"])
        flag = (f'<p class="bag__flag">{c["flag"]}</p>' if c.get("flag") else "")
        cards.append(f"""
      <article class="bag">
        <img class="bag__img" src="assets/img/bags/{c['img']}" alt="{c['alt']}"
             width="900" height="900" loading="lazy" decoding="async">
        <div class="bag__body">
          <p class="bag__kind">{c['kind']}</p>
          <h3>{c['name']}</h3>
          <p class="bag__profile">{c['profile']}</p>
          <p class="bag__note">{c['note']}</p>
          {flag}
          <dl class="bag__facts">{facts}</dl>
          <ul class="bag__prices">{prices}</ul>
          <a class="btn btn--solid bag__buy" href="{SHOP}/products/{c['buy']}">
            {icon('bag')}<span>Buy a bag</span>
            <span class="sr-only"> of {c['name']}</span></a>
        </div>
      </article>""")
    return f"""
<section class="band" id="coffee" aria-labelledby="coffee-heading">
  <div class="wrap">
    <h2 id="coffee-heading">On the shelf</h2>
    <p class="lede">Seven coffees, roasted in small batches on South Main. Every
      bag is roasted the Monday before it ships, so what arrives is days old,
      not months. Buying happens on our shop.</p>
    <div class="shelf">{"".join(cards)}</div>

    <div class="club">
      <div>
        <p class="bag__kind">Subscription</p>
        <h3>Afternoon Coffee Club</h3>
        <p>{CLUB['note']}</p>
        <p class="club__price">{CLUB['price']} &middot; ship it or collect it</p>
      </div>
      <a class="btn btn--solid" href="{SHOP}/products/{CLUB['buy']}">
        {icon('truck')}<span>Join the club</span></a>
    </div>
  </div>
</section>"""


def how():
    steps = "".join(
        f'<li><p class="step__day">{day}</p><h3>{title}</h3><p>{text}</p></li>'
        for day, title, text in STEPS)
    return f"""
<section class="band band--surface" id="how" aria-labelledby="how-heading">
  <div class="wrap">
    <div class="split">
      <div>
        <h2 id="how-heading">How a bag gets to you</h2>
        <p class="lede">Green coffee comes through Genuine Origin, Red Fox
          Coffee Merchants and Royal Coffee NYC. Everything after that happens
          here.</p>
        <ol class="steps">{steps}</ol>
      </div>
      <figure class="split__fig">
        <img src="assets/img/roastery/{ORIGIN_PHOTO[0]}" alt="{ORIGIN_PHOTO[1]}"
             width="1050" height="1400" loading="lazy" decoding="async">
        <figcaption>Green coffee on the patio at origin, before any of it
          reaches South Main.</figcaption>
      </figure>
    </div>
  </div>
</section>"""


def cafe():
    b = BUSINESS
    groups = []
    for title, items in BOARD:
        rows = "".join(
            f'<li><span class="name">{name}</span>'
            f'<span class="price">{price}</span></li>' for name, price in items)
        groups.append(f'<div class="board__grp"><h3>{title}</h3>'
                      f'<ul class="items">{rows}</ul></div>')
    return f"""
<section class="band" id="cafe" aria-labelledby="cafe-heading">
  <div class="wrap">
    <h2 id="cafe-heading">The cafe at 619 S Main</h2>
    <p class="lede">{b['cafe_name']} is the shopfront half of this: an espresso
      bar, a garden to sit in, and a case of Swallowtail Farm beef, dairy and
      cut flowers alongside the coffee. Open every day, 7:30&nbsp;AM to
      3&nbsp;PM.</p>
    <div class="board">
      <div class="board__list">{"".join(groups)}
        <p class="board__note">Prices as painted on the board in the shop.
          Specials &mdash; the matcha, the affogato, whatever is on the pastry
          plate &mdash; change and are not listed here.</p>
      </div>
      <figure class="board__fig">
        <img src="assets/img/shop/{CAFE_PHOTO[0]}" alt="{CAFE_PHOTO[1]}"
             width="1050" height="1400" loading="lazy" decoding="async">
        <figcaption>The board, as it hangs.</figcaption>
      </figure>
    </div>

    <div class="split split--tight">
      <figure class="split__fig">
        <img src="assets/img/shop/{FARM_PHOTO[0]}" alt="{FARM_PHOTO[1]}"
             width="1400" height="1050" loading="lazy" decoding="async">
      </figure>
      <div>
        <h3>Not only coffee</h3>
        <p>The freezer and the counter carry Swallowtail Farm grassfed beef and
          dairy by the cut, and there are fresh flowers most weeks. It is worth
          asking what came in.</p>
      </div>
    </div>
  </div>
</section>"""


def ratings():
    b = BUSINESS
    n = len(REVIEWS)
    slides = "".join(
        f'<div class="carou__slide" role="group" aria-roledescription="slide" '
        f'aria-label="Review {i + 1} of {n}">'
        f'{stars(5.0, 15)}<span class="sr-only">5 out of 5.</span>'
        f'<blockquote><p>{txt}</p></blockquote>'
        f'<p class="carou__who"><strong>{who}</strong><span>{when}</span></p>'
        f'</div>'
        for i, (who, when, txt) in enumerate(REVIEWS))
    cur = ' aria-current="true"'
    dots = "".join(
        f'<button class="carou__dot" type="button" data-dot="{i}"'
        f'{cur if i == 0 else ""} '
        f'aria-label="Show review {i + 1} of {n}"></button>' for i in range(n))
    arrow_l = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
               '<path d="M15.4 4.6L8 12l7.4 7.4" fill="none" stroke="currentColor" '
               'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>')
    arrow_r = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
               '<path d="M8.6 4.6L16 12l-7.4 7.4" fill="none" stroke="currentColor" '
               'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>')
    return f"""
<section class="band band--surface" id="reviews" aria-labelledby="reviews-heading">
  <div class="wrap">
    <h2 id="reviews-heading">What people say</h2>
    <div class="rating">
      <div class="rating__main">
        {stars(b['google_rating'], 24)}
        <div>
          <p class="rating__num">{b['google_rating']:.1f}<span class="sr-only"> out of 5</span></p>
          <p class="rating__meta">{b['google_count']} Google reviews</p>
        </div>
      </div>
      <div class="rating__rule" aria-hidden="true"></div>
      <div class="rating__side">
        <span>Reviews below are five-star ones, posted publicly on the
          {b['cafe_name']} Google listing.</span>
        <a href="{b['google_reviews']}">Read all {b['google_count']} on Google</a>
      </div>
    </div>

    <div class="carou" data-carousel>
      <div class="carou__vp" data-vp tabindex="0" role="group"
           aria-roledescription="carousel" aria-label="Reviews from Google">
        <div class="carou__track" data-track>{slides}</div>
      </div>
      <div class="carou__ctl">
        <button class="carou__btn" type="button" data-prev
                aria-label="Previous review">{arrow_l}</button>
        <div class="carou__dots" role="group" aria-label="Choose a review"
             data-dots>{dots}</div>
        <button class="carou__play" type="button" data-play aria-pressed="false">
          <span data-playlabel>Pause</span>
        </button>
        <button class="carou__btn" type="button" data-next
                aria-label="Next review">{arrow_r}</button>
      </div>
      <p class="sr-only" aria-live="polite" data-carou-live></p>
    </div>
  </div>
</section>"""


def gallery():
    b = BUSINESS
    imgs = "".join(
        f'<img src="assets/img/shop/{f}" alt="{a}" width="1050" height="1400" '
        f'loading="lazy" decoding="async" style="object-position:{pos}">'
        for f, a, pos in SHOP_PHOTOS)
    return f"""
<section class="band" aria-labelledby="photos-heading">
  <div class="wrap">
    <h2 id="photos-heading">The shop</h2>
    <p class="lede">Everything below is poured at {b['street']}. More goes up
      most weeks on Instagram.</p>
    <div class="gallery">{imgs}</div>
    <div class="merch">
      <img src="assets/img/bags/{MERCH['img']}" alt="{MERCH['alt']}"
           width="900" height="900" loading="lazy" decoding="async">
      <div>
        <p class="bag__kind">Merch</p>
        <h3>{MERCH['name']}</h3>
        <p>{MERCH['note']}</p>
        <p class="club__price">{MERCH['price']} &middot; {MERCH['sizes']}</p>
        <a class="btn btn--ghost" href="{SHOP}/products/{MERCH['buy']}">
          <span>See the tee</span></a>
      </div>
    </div>
    <p class="centred">
      <a class="btn btn--ig" href="{b['instagram']}">
        {icon('instagram')}<span>Follow {b['instagram_handle']}</span></a>
    </p>
  </div>
</section>"""


def faq():
    items = "".join(
        f'<details class="faq__item"><summary>{q}</summary>'
        f'<div class="faq__a"><p>{a}</p></div></details>' for q, a in FAQ)
    return f"""
<section class="band band--surface" id="faq" aria-labelledby="faq-heading">
  <div class="wrap">
    <h2 id="faq-heading">Questions</h2>
    <div class="faq">{items}</div>
  </div>
</section>"""


def visit():
    b = BUSINESS
    return f"""
<section class="band" id="visit" aria-labelledby="visit-heading">
  <div class="wrap">
    <h2 id="visit-heading">Visit the roastery</h2>
    <div class="cols">
      <div>
        <ul class="facts">
          <li>{icon('pin')}<span><span class="lbl">Address</span>
            <span class="val">{b['street']}<br>{b['city']}, {b['state']} {b['zip']}<br>
            <a href="{b['maps']}">Get directions</a> &mdash; a short walk from
            Depot Park.</span></span></li>
          <li>{icon('clock')}<span><span class="lbl">Cafe hours</span>
            <span class="val">{b['hours_text']}</span></span></li>
          <li>{icon('bag')}<span><span class="lbl">Order pickup</span>
            <span class="val">Tuesdays, 9&nbsp;AM to 5&nbsp;PM at the
            roastery. Free local delivery on Wednesdays within four
            miles.</span></span></li>
          <li>{icon('mail')}<span><span class="lbl">Email</span>
            <span class="val"><a href="mailto:{b['email']}">{b['email']}</a>
            &mdash; wholesale enquiries welcome.</span></span></li>
        </ul>
      </div>
      <div>
        <ul class="facts">
          <li>{icon('access')}<span><span class="lbl">Getting in</span>
            <span class="val">Dine in, takeaway and delivery. There is a garden
            and outdoor seating alongside the small indoor
            counter.</span></span></li>
        </ul>
        <div class="notice">
          <p><strong>Wholesale.</strong> Serving Afternoon at a restaurant, cafe
            or bar starts with an email to
            <a href="mailto:{b['email']}">{b['email']}</a>.</p>
        </div>
        <div class="notice">
          <p><strong>Something not working for you?</strong> We want everyone to
            be able to use this site and the shop. Email
            <a href="mailto:{b['email']}">{b['email']}</a> with the page you
            were on and we will fix it.</p>
        </div>
      </div>
    </div>
  </div>
</section>"""


def footer():
    b = BUSINESS
    return f"""
<footer class="ftr">
  <div class="wrap">
    <div class="ftr__in">
      <div>
        {wordmark(' mark--ftr')}
        <p>A microscopic coffee roaster and coffeeshop in Gainesville,
          Florida.</p>
        <div class="social">
          <a href="{b['instagram']}">{icon('instagram')}
            <span class="sr-only">Afternoon on Instagram</span></a>
          <a href="mailto:{b['email']}">{icon('mail')}
            <span class="sr-only">Email Afternoon Roasting</span></a>
        </div>
      </div>
      <div>
        <h2>Find us</h2>
        <ul>
          <li>{b['street']}<br>{b['city']}, {b['state']} {b['zip']}</li>
          <li><a href="{b['maps']}">Get directions</a></li>
          <li><a href="mailto:{b['email']}">{b['email']}</a></li>
          <li><a href="{b['google_reviews']}">Reviews on Google</a></li>
        </ul>
      </div>
      <div>
        <h2>Shop</h2>
        <ul>
          <li><a href="{SHOP}/collections/all">All coffee</a></li>
          <li><a href="{SHOP}/products/{CLUB['buy']}">Coffee Club</a></li>
          <li><a href="#faq">Shipping &amp; pickup</a></li>
          <li><a href="#cafe">Cafe menu</a></li>
        </ul>
      </div>
    </div>
    <p class="ftr__legal">
      <span>&copy; 2026 {b['name']}</span>
      <span>Cafe open daily 7:30 AM &ndash; 3 PM</span>
      <span>Roasted in Gainesville, Florida</span>
    </p>
  </div>
</footer>"""


# --------------------------------------------------------------------------
# Accessibility toolbar. The same component as the Dave Barber's and Brew &
# Root sites, in Afternoon's blue: a launcher and a non-modal dialog of
# display preferences, grouped into content, colour and orientation modules.
# Two rules make it safe to bolt on:
#   1. every element it draws carries .a11y-ui, and every page-wide override is
#      scoped to body > *:not(.a11y-ui), so it can never restyle its own
#      controls out from under the person using them;
#   2. the panel sizes itself in px, never rem, so the Font Size control cannot
#      shrink the buttons needed to undo it.
# --------------------------------------------------------------------------
A11Y_ICONS = {
 'person': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.6a2.1 2.1 0 1 1 0 4.2 2.1 2.1 0 0 1 0-4.2zM3.4 7.9c2.7.9 5.6 1.4 8.6 1.4s5.9-.5 8.6-1.4a1.2 1.2 0 1 1 .7 2.3c-2 .6-4 1.1-6.1 1.3l.6 3.1 2.3 5.7a1.2 1.2 0 1 1-2.2.9L13.4 16h-2.8l-2.5 6.2a1.2 1.2 0 1 1-2.2-.9l2.3-5.7.6-3.1c-2.1-.2-4.1-.7-6.1-1.3a1.2 1.2 0 1 1 .7-2.3z"/></svg>',
 'aa': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M9 16l3-8 3 8M10 13.6h4"/></svg>',
 'cursor': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 3.5l12 8.4-5.6 1 2.6 5.6-2.6 1.1-2.5-5.6-3.9 3.7z"/></svg>',
 'ls': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 5v7M11 5v7M15 5v7M3 18h18M3 18l2.5-2.5M3 18l2.5 2.5M21 18l-2.5-2.5M21 18l-2.5 2.5"/></svg>',
 'align': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 6h16M7 10.7h10M4 15.3h16M7 20h10"/></svg>',
 'bold': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M9.5 8h3.1a2.1 2.1 0 0 1 0 4.2H9.5zm0 4.2h3.6a2.1 2.1 0 0 1 0 4.2H9.5z"/></svg>',
 'sun': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2.4v2.1M12 19.5v2.1M4.2 4.2l1.5 1.5M18.3 18.3l1.5 1.5M2.4 12h2.1M19.5 12h2.1M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"/></svg>',
 'half': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 3.1a8.9 8.9 0 0 1 0 17.8z" fill="currentColor" stroke="none"/></svg>',
 'mono': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M4.3 8.6h15.4M3.2 12.4h17.6M4.3 16.2h15.4"/></svg>',
 'rline': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="2.5" y="6.5" width="19" height="11" rx="3"/><path d="M7.4 12h.01M12 12h.01M16.6 12h.01"/></svg>',
 'rmask': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 8.2c3-2.6 6-2.6 9 0s6 2.6 9 0M3 15.8c3 2.6 6 2.6 9 0s6-2.6 9 0"/></svg>',
 'noimg': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3.8 17.2L9 12l3.4 3.4M14.4 13.6L16.8 11l3.4 3.4"/><path d="M14.4 6.2l3.6 3.6M18 6.2l-3.6 3.6"/></svg>',
 'spot': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="4.5" y="4.5" width="15" height="15" rx="2"/><circle cx="4.5" cy="4.5" r="1.9" fill="currentColor" stroke="none"/><circle cx="19.5" cy="4.5" r="1.9" fill="currentColor" stroke="none"/><circle cx="4.5" cy="19.5" r="1.9" fill="currentColor" stroke="none"/><circle cx="19.5" cy="19.5" r="1.9" fill="currentColor" stroke="none"/></svg>',
 'stop': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="M5.6 18.4L18.4 5.6"/></svg>',
 'link': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M10 13.8a4 4 0 0 0 5.7 0l2.8-2.9a4 4 0 0 0-5.7-5.6l-1.3 1.3"/><path d="M14 10.2a4 4 0 0 0-5.7 0l-2.8 2.9a4 4 0 0 0 5.7 5.6l1.3-1.3"/></svg>',
 'plus': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 5.5v13M5.5 12h13"/></svg>',
 'minus': '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5.5 12h13"/></svg>',
}


def a11y_tile(key, label, ikon):
    return (f'<button class="a11y__tile" type="button" data-a11y-t="{key}" '
            f'aria-pressed="false"><span class="a11y__ic">{A11Y_ICONS[ikon]}</span>'
            f'<span class="a11y__lab" data-lab="{label}">{label}</span></button>')


def a11y_step(key, label):
    return (f'<div class="a11y__step"><span id="a11y-{key}-l">{label}</span>'
            f'<div class="a11y__row">'
            f'<button class="a11y__sbtn" type="button" data-a11y-s="{key}" data-dir="1" '
            f'aria-describedby="a11y-{key}-l" aria-label="Increase {label.lower()}">'
            f'{A11Y_ICONS["plus"]}</button>'
            f'<output class="a11y__out" id="a11y-{key}-v" for="a11y-{key}-l">Default</output>'
            f'<button class="a11y__sbtn" type="button" data-a11y-s="{key}" data-dir="-1" '
            f'aria-describedby="a11y-{key}-l" aria-label="Decrease {label.lower()}">'
            f'{A11Y_ICONS["minus"]}</button></div></div>')


def a11y_widget():
    b = BUSINESS
    content = (a11y_step('fs', 'Font Size') + a11y_tile('readable', 'Readable Font', 'aa')
               + a11y_step('lh', 'Line Height') + a11y_tile('cursor', 'Big Cursor', 'cursor')
               + a11y_tile('ls', 'Letter Spacing', 'ls')
               + a11y_tile('align', 'Align Text', 'align')
               + a11y_tile('weight', 'Font Weight', 'bold'))
    colour = (a11y_tile('c-light', 'Light Contrast', 'sun')
              + a11y_tile('c-high', 'High Contrast', 'half')
              + a11y_tile('c-mono', 'Monochrome', 'mono'))
    orient = (a11y_tile('line', 'Reading Line', 'rline')
              + a11y_tile('mask', 'Reading Mask', 'rmask')
              + a11y_tile('noimg', 'Hide Images', 'noimg')
              + a11y_tile('spot', 'Highlight Content', 'spot')
              + a11y_tile('motion', 'Stop Animations', 'stop')
              + a11y_tile('links', 'Highlight Links', 'link'))
    return f"""
<aside class="a11y-ui a11y-root" aria-label="Accessibility adjustments">
<button class="a11y-fab" id="a11yFab" type="button" aria-expanded="false"
        aria-controls="a11yPanel">{A11Y_ICONS['person']}
  <span class="sr-only">Accessibility adjustments</span>
</button>
<div class="a11y" id="a11yPanel" role="dialog" aria-labelledby="a11yTitle" hidden>
  <div class="a11y__head">
    <button class="a11y__x" type="button" data-a11y-close>
      <span aria-hidden="true">&times;</span>
      <span class="sr-only">Close accessibility adjustments</span>
    </button>
    <span class="a11y__mark">{A11Y_ICONS['person']}</span>
    <h2 id="a11yTitle">Accessibility Adjustments</h2>
    <p class="a11y__sub">{b['short']} &middot;
      <button class="a11y__hide" type="button" data-a11y-close>Hide Toolbar</button></p>
  </div>
  <div class="a11y__body">
    <section class="a11y__grp" aria-labelledby="a11yG1">
      <h3 id="a11yG1">Content Modules</h3>
      <div class="a11y__grid">{content}</div>
    </section>
    <section class="a11y__grp" aria-labelledby="a11yG2">
      <h3 id="a11yG2">Color Modules</h3>
      <div class="a11y__grid">{colour}</div>
    </section>
    <section class="a11y__grp" aria-labelledby="a11yG3">
      <h3 id="a11yG3">Orientation Modules</h3>
      <div class="a11y__grid">{orient}</div>
    </section>
    <p class="a11y__note">Your choices are stored on this device only.</p>
    <button class="a11y__reset" type="button" data-a11y-reset>Reset Settings</button>
  </div>
</div>
</aside>"""


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------
FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Atkinson+Hyperlegible:wght@400;700"
         "&family=Jost:wght@400;500;600;700"
         "&display=swap")


def build_css():
    css = (SRC / "_css.css").read_text()
    css = css.replace("TOKENS_DARK", tokens(DARK)).replace("TOKENS_LIGHT", tokens(LIGHT))
    # Longest placeholder first, so PANEL_HEAD_HOVER is not eaten by PANEL_HEAD.
    for key in sorted(PANEL, key=len, reverse=True):
        css = css.replace("PANEL_" + key.upper().replace("-", "_"), PANEL[key])
    assert "PANEL_" not in css, "unsubstituted panel colour placeholder"
    assert "TOKENS_" not in css, "unsubstituted palette placeholder"
    return css


def build_js():
    js = (SRC / "_app.js").read_text()
    return (js.replace("OPEN_HOUR", repr(BUSINESS["open_hour"]))
              .replace("CLOSE_HOUR", repr(BUSINESS["close_hour"]))
              .replace("OPEN_LABEL", json.dumps(BUSINESS["open_label"]))
              .replace("CLOSED_LABEL", json.dumps(BUSINESS["closed_label"])))


def schema():
    b = BUSINESS
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "CafeOrCoffeeShop",
        "name": b["name"],
        "alternateName": b["cafe_name"],
        "url": SHOP + "/",
        "email": b["email"],
        "image": "assets/img/icon-512.png",
        "priceRange": b["price_band"],
        "address": {"@type": "PostalAddress", "streetAddress": b["street"],
                    "addressLocality": b["city"], "addressRegion": b["state"],
                    "postalCode": b["zip"], "addressCountry": "US"},
        "openingHours": "Mo-Su 07:30-15:00",
        "servesCuisine": ["Coffee", "Espresso", "Matcha"],
        "makesOffer": [
            {"@type": "Offer",
             "itemOffered": {"@type": "Product", "name": c["name"]},
             "price": c["prices"][0][1].lstrip("$"), "priceCurrency": "USD",
             "url": f"{SHOP}/products/{c['buy']}"}
            for c in COFFEES],
        "aggregateRating": {"@type": "AggregateRating",
                            "ratingValue": b["google_rating"],
                            "reviewCount": b["google_count"]},
        "sameAs": [b["instagram"]],
        "publicAccess": True,
    }, indent=1)


def faq_schema():
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQ],
    }, indent=1)


def body():
    return "\n".join([
        '<a class="skip" href="#main-content">Skip to main content</a>',
        header(),
        '<main id="main-content">',
        hero(), coffee(), how(), cafe(), ratings(), gallery(), faq(), visit(),
        '</main>',
        footer(),
        a11y_widget(),
    ])


DESC = ("Small-batch coffee roaster and coffeeshop at 619 S Main St, "
        "Gainesville, Florida. Roasted Mondays, shipped Tuesdays. Espresso bar "
        "open daily 7:30 AM to 3 PM.")


def main():
    print("Checking colour contrast against WCAG 2.1 AA:")
    check_contrast()

    css, js, mark = build_css(), build_js(), body()
    title = f"{BUSINESS['name']} — Gainesville, Florida"

    head_shared = (
        f'<title>{title}</title>\n'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONTS}">\n'
        f'<style>{css}</style>'
    )

    standalone = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, '
        'viewport-fit=cover">\n'
        f'<meta name="description" content="{DESC}">\n'
        '<meta name="theme-color" content="#0D1420">\n'
        '<link rel="icon" href="assets/img/icon-512.png" sizes="256x256">\n'
        '<link rel="apple-touch-icon" href="assets/img/icon-512.png">\n'
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:description" content="{DESC}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:image" content="assets/img/icon-512.png">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'{head_shared}\n'
        f'<script type="application/ld+json">{schema()}</script>\n'
        f'<script type="application/ld+json">{faq_schema()}</script>\n'
        '</head>\n<body>\n'
        f'{mark}\n'
        f'<script>{js}</script>\n'
        '</body>\n</html>\n'
    )

    # The Artifact host wraps a body fragment in its own document skeleton, so
    # this variant carries no <head> and must never be served as a page.
    fragment = f'{head_shared}\n{mark}\n<script>{js}</script>\n'

    (ROOT / "index.html").write_text(standalone)
    (ROOT / "artifact.html").write_text(fragment)
    print(f"\nindex.html    {len(standalone) / 1024:6.1f} KB")
    print(f"artifact.html {len(fragment) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
