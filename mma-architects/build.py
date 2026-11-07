#!/usr/bin/env python3
"""Generates the MMA Architects site: full pages in French, English, Spanish and Arabic, and one Chinese landing page.

Spanish, Arabic and Chinese text lives in translations.py. Run: python3 build.py"""
import json
from html import escape
from pathlib import Path

from translations import TR, ZH

ROOT = Path(__file__).parent
PHONES = [("06 61 22 50 67", "212661225067"), ("06 33 93 15 42", "212633931542")]
# Plot Lab map layers. Check the "Going public" list in README.md before launch: the imagery needs a licence for commercial use.
IMAGERY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
IMAGERY_CREDIT = "Imagery © Esri, Maxar, Earthstar Geographics"
STREET_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
STREET_CREDIT = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
LANG = "en"
PREFIX = ""
OTHER_PATH = ""
FULL_LANGS = ("fr", "en", "es", "ar")
ZH_PAGES = ("index.html", "plot-lab.html")  # the only pages that exist in Chinese
ZH_LANDING = True  # whether the Chinese page being built is the landing page, which holds the section anchors
# code, name in its own language, label in the switch
SWITCH = (("fr", "Français", "FR"), ("en", "English", "EN"), ("es", "Español", "ES"), ("ar", "العربية", "عربي"), ("zh", "中文", "中文"))
LOCALES = {"fr": "fr-FR", "en": "en-GB", "es": "es-ES", "ar": "en-GB", "zh": "en-GB"}
FONTS = {
    "ar": "family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&family=Noto+Kufi+Arabic:wght@300;400;500",
    "zh": "family=Noto+Sans+SC:wght@300;400;500;600",
}
LATIN_FONTS = "family=Geologica:SHRP,wght@0..100,200..600&family=Instrument+Sans:wght@400;500;600"
MISSING = set()


def t(en, fr):
    if LANG == "en":
        return en
    if LANG == "fr":
        return fr
    entry = ZH.get(en) if LANG == "zh" else TR.get(en)
    if entry is None:
        MISSING.add((LANG, en))
        return en
    return entry if LANG == "zh" else entry[0 if LANG == "es" else 1]


def pick(pair):
    """Translate an (English, French) pair from the project data."""
    return t(pair[0], pair[1])


def num(n):
    s = f"{n:,}"
    if LANG == "fr":
        return s.replace(",", " ")
    if LANG == "es":
        return s.replace(",", ".") if n >= 10000 else str(n)
    return s


def phone_text(i):
    """A phone number that stays in reading order inside Arabic text. Visitors likely abroad get the international form."""
    local, digits = PHONES[i]
    shown = local if LANG in ("fr", "en") else f"+212 {digits[3:6]} {digits[6:8]} {digits[8:10]} {digits[10:12]}"
    return f'<span dir="ltr">{shown}</span>'


def img(name):
    return f"{PREFIX}assets/img/{name}.webp"


def url(path):
    """Link to a page in the current language. Chinese pages that don't exist fall back to the landing page's contact section."""
    if LANG == "zh":
        if path in ZH_PAGES:
            return f"{PREFIX}zh/{path}"
        anchor = path if path.startswith("#") else "#contact"
        return anchor if ZH_LANDING else f"{PREFIX}zh/index.html{anchor}"
    return f"{PREFIX}{LANG}/{path}"


ARROW = '<span class="arr" aria-hidden="true">&rarr;</span>'


def btn(label, href, cls=""):
    return f'<a class="btn {cls}" href="{href}">{label} {ARROW}</a>'


def wa_link(text):
    from urllib.parse import quote
    return f"https://wa.me/{PHONES[0][1]}?text={quote(text)}"


# ---------------------------------------------------------------- Projects
PROJECTS = [
    dict(slug="residential-tower-tangier", type="apartments", cover="tower-1", hero="tower-1",
         name=("Residential tower", "Tour résidentielle"), place=("Tangier", "Tanger"),
         kind=("Apartments", "Appartements"),
         pitch=("A restricted plot, turned into a landmark.", "Un terrain contraint, devenu un repère."),
         text=("The plot covers 4,604 m², but the planning rules left only 1,353 m² to build on. Rather than lose the project, we shaped the tower around those limits, about two minutes on foot from Tanger Ville station.",
               "Le terrain couvre 4 604 m², mais les règles d'urbanisme n'en laissent que 1 353 m² constructibles. Plutôt que de perdre le projet, nous avons dessiné la tour autour de ces limites, à environ deux minutes à pied de la gare Tanger Ville."),
         specs=[(("Plot on paper", "Terrain sur le papier"), 4604, "m²"), (("Buildable after the rules", "Constructible après les règles"), 1353, "m²"), (("Station on foot", "Gare à pied"), None, ("about 2 min", "environ 2 min"))],
         gallery=[("g-full", "tower-2"), ("g-7", "tower-3")],
         diagrams=["tower-d1", "tower-d2", "tower-d3", "tower-d4"], plan="tower-plan"),
    dict(slug="hotel-chefchaouen", type="hospitality", cover="hotel-dusk", hero="hotel-dusk",
         name=("4-star hotel", "Hôtel 4 étoiles"), place=("Chefchaouen", "Chefchaouen"),
         kind=("Hospitality", "Hôtellerie"),
         pitch=("A hotel that steps with the mountain.", "Un hôtel qui s'étage avec la montagne."),
         text=("A terraced 4-star hotel in the hills of Chefchaouen. The design runs from the arrival sequence and lobby through to rooms framed on the mountains, so the view becomes part of what the hotel sells.",
               "Un hôtel 4 étoiles en terrasses sur les hauteurs de Chefchaouen. Le projet va de l'arrivée et du hall jusqu'aux chambres cadrées sur les montagnes : la vue devient une part de ce que l'hôtel vend."),
         specs=[(("Total floor area", "Surface de plancher"), 6250, "m²"), (("Plot", "Terrain"), 3360, "m²"), (("Basement", "Sous-sol"), 1438, "m²"), (("Parking", "Parking"), None, ("about 22 spaces", "environ 22 places"))],
         compare=("hotel-day", "hotel-dusk", ("Day", "Jour"), ("Dusk", "Crépuscule")),
         gallery=[("g-full", "hotel-2"), ("g-7", "hotel-3"), ("g-5", "hotel-4")]),
    dict(slug="180-apartments-tangier", type="apartments", cover="apartments-day", hero="apartments-dusk",
         name=("180-apartment building", "Immeuble de 180 appartements"), place=("Tangier", "Tanger"),
         kind=("Apartments", "Appartements"),
         pitch=("180 homes close to the sea and the TGV.", "180 logements entre la mer et le TGV."),
         text=("A large residential building close to the seafront and the TGV station. Apartments range from 60 to 150 m² over two levels of underground parking, with a public square given back to the neighbourhood.",
               "Un grand immeuble résidentiel proche du front de mer et de la gare TGV. Les appartements vont de 60 à 150 m², sur deux niveaux de parking en sous-sol, avec une place rendue au quartier."),
         specs=[(("Total floor area", "Surface de plancher"), 27024, "m²"), (("Plot", "Terrain"), 3166, "m²"), (("Apartments", "Appartements"), 180, ""), (("Apartment sizes", "Surface des logements"), None, ("60–150 m²", "60–150 m²")), (("Parking", "Parking"), None, ("79 spaces", "79 places"))],
         compare=("apartments-day", "apartments-dusk", ("Morning", "Matin"), ("Sunset", "Coucher de soleil")), gallery=[]),
    dict(slug="villa-guest-house-estate", type="villas", cover="estate-dusk", hero="estate-dusk",
         name=("Villas and guest house estate", "Domaine de villas et maison d'hôtes"), place=None,
         kind=("Villas", "Villas"),
         pitch=("One estate, planned as a whole.", "Un domaine, pensé comme un tout."),
         text=("Detached villas, a guest house, a covered hall and an event space, set out together around shared gardens. Planning them as one estate is what keeps each building private while the site works as a whole.",
               "Des villas isolées, une maison d'hôtes, un préau couvert et une salle de fêtes, organisés autour de jardins communs. C'est en les pensant comme un seul domaine que chaque bâtiment reste intime et que le site fonctionne."),
         specs=[], compare=("estate-dusk", "estate-night", ("Sunset", "Coucher de soleil"), ("Night", "Nuit")),
         gallery=[("g-full", "estate-2")], plan="estate-plan"),
    dict(slug="villa-maresvista", type="villas", cover="maresvista-1", hero="maresvista-1",
         name=("Villa Maresvista", "Villa Maresvista"), place=("Sidi Mghayt", "Sidi Mghayt"),
         kind=("Villas", "Villas"),
         pitch=("A white villa built around one view.", "Une villa blanche, construite autour d'une vue."),
         text=("A low, white villa organised around its pool and a single framed view of the sea. The terrace does the selling: shade, water and the horizon, all in one composition.",
               "Une villa blanche et basse, organisée autour de sa piscine et d'une vue cadrée sur la mer. La terrasse fait tout : l'ombre, l'eau et l'horizon, dans une seule composition."),
         specs=[], gallery=[("g-full", "maresvista-3"), ("g-7", "maresvista-2"), ("g-5", "maresvista-4")]),
    dict(slug="beachfront-resort", type="hospitality", cover="resort-3", hero="resort-1",
         name=("Beachfront resort", "Complexe en front de mer"), place=None,
         kind=("Hospitality", "Hôtellerie"),
         pitch=("Feet in the sand, by design.", "Les pieds dans le sable, par le dessin."),
         text=("A curved resort building with direct access to the beach. Its long terraces open every room and pool toward the water, turning the site's greatest asset into the guest's first impression.",
               "Un bâtiment courbe avec un accès direct à la plage. Ses longues terrasses ouvrent chaque chambre et chaque piscine vers l'eau : le premier atout du site devient la première impression du client."),
         specs=[], gallery=[("g-full", "resort-2"), ("g-7", "resort-4"), ("g-5", "resort-5"), ("g-5", "resort-6"), ("g-7", "resort-8")]),
    dict(slug="residence-alma", type="apartments", cover="alma-night", hero="alma-night",
         name=("Résidence Alma", "Résidence Alma"), place=None,
         kind=("Apartments", "Appartements"),
         pitch=("Big homes on a small triangular plot.", "De grands logements sur un petit terrain triangulaire."),
         text=("A compact apartment building that fits generous homes onto a triangular plot. Hard geometry is where good planning pays: every corner of the floor plate is put to work.",
               "Un immeuble compact qui installe de grands logements sur un terrain triangulaire. C'est sur les géométries difficiles que le plan fait la différence : chaque angle de l'étage est mis au travail."),
         specs=[], compare=("alma-dawn", "alma-night", ("Dawn", "Aube"), ("Night", "Nuit")), gallery=[], plan="alma-plan"),
    dict(slug="suites-tower", type="hospitality", cover="suites-1", hero="suites-1",
         name=("Suites tower", "Tour de suites"), place=None,
         kind=("Hospitality", "Hôtellerie"),
         pitch=("A façade people remember.", "Une façade qu'on n'oublie pas."),
         text=("A tower of suites with a sculpted, wave-like façade, shared terraces and a generous pool deck. In a competitive market, a building that is instantly recognisable is part of the investment.",
               "Une tour de suites à la façade sculptée en vagues, avec terrasses communes et un grand deck de piscine. Sur un marché concurrentiel, un bâtiment reconnaissable au premier regard fait partie de l'investissement."),
         specs=[], gallery=[("g-full", "suites-4"), ("g-7", "suites-5"), ("g-5", "suites-6"), ("g-full", "suites-7")], plan="suites-plan"),
]

TYPES = [
    ("home", "maresvista-1", ("A villa or family home", "Une villa ou une maison familiale"),
     ("Does it suit the plot, your budget and the way you will live in it?", "Convient-elle au terrain, à votre budget et à votre façon d'y vivre ?"), "villa-maresvista"),
    ("rental", "apartments-day", ("An apartment building", "Un immeuble d'appartements"),
     ("How many homes can it hold, and which layouts will rent or sell best?", "Combien de logements peut-il accueillir, et quels plans se loueront ou se vendront le mieux ?"), "180-apartments-tangier"),
    ("hospitality", "hotel-dusk", ("A hotel or guest house", "Un hôtel ou une maison d'hôtes"),
     ("Can the site carry the rooms, circulation and services the business needs?", "Le site peut-il porter les chambres, les circulations et les services de l'activité ?"), "hotel-chefchaouen"),
    ("estate", "estate-dusk", ("A multi-building estate", "Un domaine de plusieurs bâtiments"),
     ("How do the buildings share one site while staying private?", "Comment plusieurs bâtiments partagent-ils un site en restant intimes ?"), "villa-guest-house-estate"),
    ("interior", "resort-6", ("Interior design", "L'architecture d'intérieur"),
     ("Do the rooms, materials and light suit the way the space will be used?", "Les pièces, les matériaux et la lumière sont-ils adaptés à l'usage du lieu ?"), "beachfront-resort"),
]


def p_name(p):
    return pick(p["name"])


def p_place(p):
    return pick(p["place"]) if p["place"] else ""


def p_kind(p):
    return pick(p["kind"])


def p_meta(p):
    return " · ".join(x for x in (p_place(p), p_kind(p)) if x)


def by_slug(slug):
    return next(p for p in PROJECTS if p["slug"] == slug)


def pcard(p, view_name=True, prefix_extra=""):
    vt = f' style="view-transition-name:p-{p["slug"]}"' if view_name else ""
    label = t("View", "Voir")
    return f'''<a class="pcard" href="{url("projects/" + p["slug"] + ".html")}" data-type="{p["type"]}" data-cursor="{label}">
  <div class="pcard-media"><img src="{img(p["cover"])}" alt="{escape(p_name(p))}" loading="lazy"{vt}></div>
  <div class="pcard-info"><h3>{escape(p_name(p))}</h3><span>{escape(p_meta(p))}</span></div>
</a>'''


def compare_block(cmp, cls="", tease=False):
    a, b, la, lb = cmp
    la, lb = pick(la), pick(lb)
    label = t("Drag to change the time of day", "Faites glisser pour changer l'heure")
    return f'''<div class="compare {cls}"{' data-tease' if tease else ''}>
  <img src="{img(a)}" alt="{escape(la)}" loading="lazy">
  <div class="after"><img src="{img(b)}" alt="{escape(lb)}" loading="lazy"></div>
  <div class="compare-line"></div><div class="compare-handle" aria-hidden="true"></div>
  <span class="compare-tag l">{escape(la)}</span><span class="compare-tag r">{escape(lb)}</span>
  <input type="range" min="0" max="100" value="50" aria-label="{label}">
</div>'''


# ---------------------------------------------------------------- Layout
def nav_links():
    if LANG == "zh":
        return [("#services", "服务范围", "services"), ("#work", "项目案例", "work"), ("plot-lab.html", "地块实验室", "lab"), ("#process", "合作流程", "process")]
    return [("projects.html", t("Projects", "Projets"), "projects"), ("plot-lab.html", t("Plot Lab", "Plot Lab"), "lab"),
            ("expertise.html", t("Expertise", "Expertise"), "expertise"), ("studio.html", t("Studio", "Studio"), "studio")]


def lang_switch(path):
    """Language switch: the current language is marked, the others link to the same page (or the Chinese landing page if it has no Chinese version)."""
    parts = []
    for code, name, label in SWITCH:
        if code == LANG:
            parts.append(f'<span aria-current="true" aria-label="{name}">{label}</span>')
        else:
            target = "index.html" if code == "zh" and path not in ZH_PAGES else path
            parts.append(f'<a href="{PREFIX}{code}/{target}" hreflang="{code}" lang="{code}" aria-label="{name}">{label}</a>')
    return f'<div class="lang" role="group" aria-label="{t("Language", "Langue")}">{"".join(parts)}</div>'


def layout(path, title, desc, main, active="", extra_head="", extra_js="", i18n=None):
    global OTHER_PATH
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="{PREFIX}{c}/{path}">\n' for c in FULL_LANGS + (("zh",) if path in ZH_PAGES else ()) if c != LANG)
    fonts = f"{LATIN_FONTS}&{FONTS[LANG]}" if LANG in FONTS else LATIN_FONTS
    links = "".join(f'<a href="{url(h)}"{" aria-current=page" if k == active else ""}>{escape(l)}</a>' for h, l, k in nav_links())
    mobile = "".join(f'<a class="display" href="{url(h)}">{escape(l)}</a>' for h, l, k in nav_links())
    i18n_tag = f"<script>window.MMA_I18N={json.dumps(i18n, ensure_ascii=False)}</script>" if i18n else ""
    wa = wa_link(t("Hello MMA, I would like to talk about a project.", "Bonjour MMA, je souhaite parler d'un projet."))
    return f'''<!doctype html>
<html lang="{LANG}"{' dir="rtl"' if LANG == "ar" else ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="theme-color" content="#0B1A1F">
{alternates}<link rel="alternate" hreflang="x-default" href="{PREFIX}fr/{path}">
<link rel="icon" href="{PREFIX}assets/logo-mma-white.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{PREFIX}css/site.css">
<script>document.documentElement.classList.add('js')</script>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}}}</script>
{extra_head}
</head>
<body>
<a class="skip" href="#main">{t("Skip to content", "Aller au contenu")}</a>
<div class="wipe" aria-hidden="true"><img src="{PREFIX}assets/logo-mma-white.png" alt=""></div>
<header class="head">
  <a class="logo" href="{url("index.html")}"><img src="{PREFIX}assets/logo-mma-white.png" alt="MMA, Mharrech Mribah Architects" width="500" height="172"></a>
  <nav class="nav" aria-label="{t("Main", "Principal")}">
    {links}
    {lang_switch(path)}
    <a class="btn" href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a>
    <button class="menu-btn" type="button" aria-label="{t("Menu", "Menu")}" aria-expanded="false"><span></span><span></span></button>
  </nav>
</header>
<div class="mobile-menu">
  {mobile}
  <a class="display" href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a>
  {lang_switch(path)}
</div>
<main id="main">
{main}
</main>
<footer class="foot">
  <div class="foot-grid">
    <div><img class="foot-logo" src="{PREFIX}assets/logo-full-white.png" alt="MMA, Mharrech Mribah Architects" loading="lazy"></div>
    <div><h4>{t("Explore", "Explorer")}</h4><ul>{"".join(f'<li><a href="{url(h)}">{escape(l)}</a></li>' for h, l, k in nav_links())}</ul></div>
    <div><h4>{t("Talk to us", "Nous parler")}</h4><ul>
      <li><a href="tel:+{PHONES[0][1]}">{phone_text(0)}</a></li>
      <li><a href="tel:+{PHONES[1][1]}">{phone_text(1)}</a></li>
      <li><a href="{wa}" target="_blank" rel="noopener">WhatsApp</a></li>
    </ul></div>
    <div><h4>{t("Studio", "Studio")}</h4><ul><li>{t("Tangier, Morocco", "Tanger, Maroc")}</li><li><a href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a></li></ul></div>
  </div>
  <div class="foot-end"><span dir="ltr">© 2026 MMA, Mharrech Mribah Architects</span><span>{t("Images are design visualizations.", "Les images sont des visualisations du projet.")}</span></div>
</footer>
<div class="dock">
  <div class="dock-menu">
    <a href="{wa}" target="_blank" rel="noopener">WhatsApp</a>
    <a href="tel:+{PHONES[0][1]}">{phone_text(0)}</a>
    <a href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a>
  </div>
  <button class="dock-btn" type="button" aria-expanded="false" aria-label="{t("Talk to an architect", "Parler à un architecte")}"><i></i><span>{t("Talk to an architect", "Parler à un architecte")}</span></button>
</div>
<div class="cursor" aria-hidden="true"></div>
{i18n_tag}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.13/dist/lenis.min.js"></script>
<script src="{PREFIX}js/site.js"></script>
{extra_js}
</body>
</html>
'''


def final_cta(image="maresvista-3"):
    primary = btn(t("Start your project", "Lancer votre projet"), url("contact.html"))
    return f'''<section class="final">
  <img src="{img(image)}" alt="" loading="lazy" data-parallax="5">
  <div class="final-body">
    <h2 class="display d-l" data-lines>{t("Bring us the plot. We'll show you what it can become.", "Apportez le terrain. Nous vous montrons ce qu'il peut devenir.")}</h2>
    <div class="btn-row" data-reveal>{primary}{btn(t("Test it in 3D first", "Le tester d'abord en 3D"), url("plot-lab.html"), "ghost")}</div>
  </div>
</section>'''


# ---------------------------------------------------------------- Process
def stages():
    """The six stages: name, what we do, the promise, what the client receives."""
    return [
        (t("Feasibility", "Faisabilité"), t("We read the planning rules and test what the plot can really hold, before you commit further.", "Nous lisons les règles d'urbanisme et testons ce que le terrain peut réellement accueillir, avant d'aller plus loin."),
         t("Know what your plot can really hold.", "Sachez ce que votre terrain peut vraiment accueillir."), t("A clear feasibility study", "Une étude de faisabilité claire")),
        (t("Concept", "Esquisse"), t("Layouts, volumes and 3D views you can compare and react to.", "Plans, volumes et vues 3D à comparer et à commenter."),
         t("See it before you decide.", "Voyez-le avant de décider."), t("3D options to compare", "Des options 3D à comparer")),
        (t("Developed design", "Avant-projet"), t("The chosen concept, measured and coordinated: plans, sections, façades, materials.", "L'esquisse retenue, mesurée et coordonnée : plans, coupes, façades, matériaux."),
         t("Your choice, made precise.", "Votre choix, rendu précis."), t("A coordinated set of drawings", "Un dossier de plans coordonné")),
        (t("Building permit", "Permis de construire"), t("We prepare and file the application, then follow it with the authorities.", "Nous préparons et déposons le dossier, puis nous le suivons auprès des autorités."),
         t("We handle the paperwork.", "Les démarches, nous nous en chargeons."), t("An application filed and followed", "Un dossier déposé et suivi")),
        (t("Contractors", "Entreprises"), t("Construction documents and comparable quotes, with a clear recommendation.", "Dossier d'exécution et devis comparables, avec une recommandation claire."),
         t("Compare like with like.", "Comparez ce qui est comparable."), t("Comparable quotes and a recommendation", "Des devis comparables et une recommandation")),
        (t("Site supervision", "Suivi de chantier"), t("Regular visits and reports through to handover.", "Visites régulières et comptes rendus jusqu'à la réception."),
         t("What was drawn gets built.", "Ce qui est dessiné est construit."), t("Reports through to handover", "Des comptes rendus jusqu'à la réception")),
    ]


def iso_windows():
    """Window panes on the two visible faces of the drawn building."""
    out = ""
    for x0, x1, base in ((82, 94, 130), (100, 112, 130), (128, 140, 154), (146, 158, 154)):
        origin, slope = (74, 24 / 46) if base == 130 else (120, -24 / 46)
        for d0, d1 in ((6, 16), (28, 38), (50, 60)):
            y = lambda x, d: round(base + (x - origin) * slope - d, 1)
            out += f'<polygon points="{x0},{y(x0, d1)} {x1},{y(x1, d1)} {x1},{y(x1, d0)} {x0},{y(x0, d0)}"/>'
    return out


# (first stage shown, last stage shown, kind, drawing). "d" lines draw themselves, "f" shapes fade in.
ISO_LAYERS = [
    (1, 6, "f iso-sun", '<polygon stroke-dasharray="4 4" points="120,93.6 190,130 120,166.4 50,130"/>'),
    (6, 6, "f iso-shadow", '<polygon points="74,130 120,154 84,172 38,148"/>'),
    (2, 6, "f iso-mask", '<polygon points="74,64 120,40 166,64 166,130 120,154 74,130"/>'),
    (2, 6, "d", '<path pathLength="1" d="M74 64 120 40 166 64 120 88ZM74 64V130L120 154 166 130V64M120 88V154"/>'),
    (3, 6, "d", '<path pathLength="1" d="M74 86 120 110 166 86M74 108 120 132 166 108"/>'),
    (4, 5, "d iso-sun", '<path pathLength="1" d="M24 44a16 16 0 1 0 32 0a16 16 0 1 0-32 0M32 44l6 6 11-12"/>'),
    (5, 5, "d", '<path pathLength="1" d="M190 130V26M160 36H226M190 26 168 36M190 26 214 36M172 36V58M168 58H176"/>'),
    (6, 6, "f iso-lit", iso_windows()),
    (6, 6, "f iso-lit", '<circle cx="212" cy="30" r="10"/>'),
    (6, 6, "f iso-tree", '<circle cx="56" cy="124" r="5"/><circle cx="184" cy="136" r="6"/><circle cx="170" cy="150" r="4"/>'),
]


def iso(stage=6, cls="path-iso"):
    """The building at a given stage. The main drawing carries every layer so the script can step through them."""
    layers = ""
    for first, last, kind, shape in ISO_LAYERS:
        on = first <= stage <= last
        if cls == "path-iso":
            layers += f'<g class="{kind}{" on" if on else ""}" data-from="{first}" data-until="{last}">{shape}</g>'
        elif on:
            layers += f'<g class="{kind} on{" new" if first == stage else ""}">{shape}</g>'
    return f'<svg class="iso {cls}" viewBox="0 0 240 190" aria-hidden="true"><polygon points="120,78 220,130 120,182 20,130"/>{layers}</svg>'


def book_btn(cls=""):
    """Booking goes through WhatsApp. Replace this link to use a calendar instead."""
    href = wa_link(t("Hello MMA, I would like to book the free 30-minute discovery call.", "Bonjour MMA, je souhaite réserver l'appel découverte gratuit de 30 minutes."))
    return f'<a class="btn {cls}" href="{href}" target="_blank" rel="noopener">{t("Book my free call", "Réserver mon appel gratuit")} {ARROW}</a>'


def process_section():
    steps = ""
    for n, (name, desc, hook, get) in enumerate(stages(), 1):
        label = t("Stage {n} of 6 · {name}", "Étape {n} sur 6 · {name}").format(n=n, name=name)
        steps += f'''<li class="path-step" data-now="{escape(label, quote=True)}">
      <span class="path-n" aria-hidden="true">{n}</span>
      {iso(n, "path-thumb")}
      <div class="path-body">
        <h4>{escape(name)}</h4>
        <p class="path-hook">{escape(hook)}</p>
        <p class="path-desc">{escape(desc)}</p>
        <p class="path-get"><span>{t("You get", "Vous obtenez")}</span>{escape(get)}</p>
      </div>
    </li>'''
    perks = "".join(f"<li>{p}</li>" for p in (t("30 minutes", "30 minutes"), t("Free", "Gratuit"), t("No obligation", "Sans engagement")))
    agenda = "".join(f"<li>{p}</li>" for p in (
        t("Tell us about your plot, your goal and your budget", "Parlez-nous de votre terrain, de votre objectif et de votre budget"),
        t("Get an architect's first read of your project", "Recevez le premier avis d'un architecte sur votre projet"),
        t("Leave knowing the right next step", "Repartez en sachant quelle est la bonne prochaine étape")))
    return f'''<section class="wrap path" id="process" data-path>
  <div class="path-intro">
    <span class="eyebrow">{t("How it works", "Comment ça se passe")}</span>
    <h2 class="display d-m" data-lines>{t("It all starts with a free 30-minute call.", "Tout commence par un appel gratuit de 30 minutes.")}</h2>
    <p class="lede" data-reveal>{t("Talk your project through with an architect, at no cost. If it makes sense to go further, six clear stages take you from the plot to the handover, with one team beside you.", "Parlez de votre projet avec un architecte, sans frais. S'il est utile d'aller plus loin, six étapes claires vous mènent du terrain à la réception, avec une seule équipe à vos côtés.")}</p>
    <div class="path-visual">
      {iso()}
      <span class="path-now" aria-hidden="true">{t("From the plot to the handover", "Du terrain à la réception")}</span>
    </div>
    <div class="path-cta" data-reveal>{book_btn()}<a class="link" href="{url("contact.html")}">{t("Or write your brief first", "Ou préparez d'abord votre brief")}</a></div>
    <ul class="path-perks">{perks}</ul>
  </div>
  <div class="path-flow">
    <div class="path-call" data-reveal>
      <div class="dial" aria-hidden="true">
        <svg viewBox="0 0 120 120"><circle class="dial-ticks" cx="60" cy="60" r="54" pathLength="60"/><circle class="dial-arc" cx="60" cy="60" r="54" pathLength="60"/></svg>
        <div class="dial-n"><strong data-count="30">30</strong><small>{t("min", "min")}</small></div>
      </div>
      <div>
        <span class="eyebrow">{t("Where it all starts", "Le point de départ")}</span>
        <h3 class="display d-s">{t("Your free discovery call", "Votre appel découverte gratuit")}</h3>
        <ul class="path-agenda">{agenda}</ul>
      </div>
    </div>
    <h3 class="display d-m path-sub" data-lines>{t("Then six stages, one team.", "Puis six étapes, une seule équipe.")}</h3>
    <div class="path-track"><span class="path-fill" aria-hidden="true"></span><ol class="path-steps">{steps}</ol></div>
    <p class="lede path-note" data-reveal>{t("You approve each stage before the next begins. You can start with the feasibility study alone, then decide.", "Vous validez chaque étape avant la suivante. Vous pouvez commencer par la seule étude de faisabilité, puis décider.")}</p>
    <div class="path-end" data-reveal>
      <p class="display d-s">{t("The first step takes 30 minutes and costs nothing.", "La première étape prend 30 minutes et ne coûte rien.")}</p>
      {book_btn("ink")}
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------- Home
def page_home():
    slides = [("estate-dusk", "villa-guest-house-estate"), ("suites-1", "suites-tower"), ("hotel-dusk", "hotel-chefchaouen"),
              ("maresvista-1", "villa-maresvista"), ("resort-3", "beachfront-resort")]
    hero = ""
    for i, (im, slug) in enumerate(slides):
        p = by_slug(slug)
        cap = f'<a href="{url("projects/" + slug + ".html")}"><strong>{escape(p_name(p))}</strong>{(" · " + escape(p_place(p))) if p["place"] else ""}</a>'
        hero += f'<div class="hero-slide" data-caption="{escape(cap, quote=True)}"><img src="{img(im)}" alt="{escape(p_name(p))}"{" fetchpriority=high" if i == 0 else ""}></div>'
    bars = "".join(f'<button type="button" aria-label="{escape(p_name(by_slug(s)))}"><i></i></button>' for _, s in slides)

    rail_order = ["residential-tower-tangier", "hotel-chefchaouen", "180-apartments-tangier", "villa-guest-house-estate", "villa-maresvista", "beachfront-resort", "residence-alma", "suites-tower"]
    rail = "".join(pcard(by_slug(s)) for s in rail_order)

    marquee_items = [(f"{num(27024)} {t('m²', 'm²')}", t("largest scheme", "plus grand projet")), ("180", t("apartments in one building", "appartements dans un immeuble")),
                     (t("4 stars", "4 étoiles"), t("hotel in Chefchaouen", "hôtel à Chefchaouen")), (t("2 min", "2 min"), t("from the TGV station", "de la gare TGV")),
                     (t("8 projects", "8 projets"), t("in the selected works", "dans la sélection"))]
    marquee = "".join(f"<span>{escape(a)} <small>{escape(b)}</small></span>" for a, b in marquee_items)

    type_rows = ""
    float_imgs = ""
    for key, im, title, q, slug in TYPES:
        type_rows += f'<a class="type" data-float="{key}" href="{url("expertise.html")}#{key}"><span class="display d-m">{escape(pick(title))}</span><p class="muted">{escape(pick(q))}</p></a>'
        float_imgs += f'<img src="{img(im)}" data-key="{key}" alt="" loading="lazy">'

    main = f'''
<section class="hero">
  {hero}
  <div class="hero-body">
    <h1 class="display d-xl" data-lines>{t("Design the investment, not just the building.", "Concevez l'investissement, pas seulement le bâtiment.")}</h1>
    <div class="hero-foot">
      <div data-reveal>
        <p class="lede">{t("MMA is an architecture practice for people investing in Moroccan property: homes, apartment buildings, hotels and estates.", "MMA est un cabinet d'architecture pour celles et ceux qui investissent dans l'immobilier au Maroc : maisons, immeubles, hôtels et domaines.")}</p>
        <div class="btn-row">{btn(t("Test your plot in 3D", "Testez votre terrain en 3D"), url("plot-lab.html"))}{btn(t("See the projects", "Voir les projets"), url("projects.html"), "ghost")}</div>
      </div>
    </div>
    <div class="hero-meta"><span class="hero-caption"></span><div class="hero-bars">{bars}</div></div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{marquee}</div></div>

<section class="section wrap before-wall">
  <h2 class="display d-l" data-lines>{t("Money is made or lost before the first wall.", "L'argent se gagne ou se perd avant le premier mur.")}</h2>
  <ol class="bw-steps">
    <li data-reveal>
      <svg class="bw-draw" viewBox="0 0 200 130" aria-hidden="true"><polygon points="100,30 185,75 100,120 15,75"/><polygon class="bw-sun" stroke-dasharray="4 4" points="100,55 138,75 100,95 62,75"/></svg>
      <span class="bw-axis" aria-hidden="true"></span>
      <div><h3 class="display d-s">{t("The plot", "Le terrain")}</h3><p class="muted">{t("What it allows", "Ce qu'il permet")}</p></div>
    </li>
    <li data-reveal>
      <svg class="bw-draw" viewBox="0 0 200 130" aria-hidden="true"><polygon class="bw-faint" points="100,30 185,75 100,120 15,75"/><path class="bw-sun" d="M100 10 138 30 100 50 62 30Z M62 30V75L100 95V50M138 30V75L100 95"/><path d="M62 45 100 65 138 45M62 60 100 80 138 60"/></svg>
      <span class="bw-axis" aria-hidden="true"></span>
      <div><h3 class="display d-s">{t("The building", "Le bâtiment")}</h3><p class="muted">{t("What it can hold", "Ce qu'il peut contenir")}</p></div>
    </li>
    <li data-reveal>
      <svg class="bw-draw" viewBox="0 0 200 130" aria-hidden="true"><polygon class="bw-faint" points="100,30 185,75 100,120 15,75"/><polygon class="bw-shadow" points="62,75 100,95 80,105 42,85"/><path d="M100 10 138 30 100 50 62 30Z M62 30V75L100 95V50M138 30V75L100 95"/><polygon class="bw-lit" points="110,57 128,47.5 128,57.5 110,67"/><circle class="bw-lit" cx="172" cy="22" r="9"/></svg>
      <span class="bw-axis" aria-hidden="true"></span>
      <div><h3 class="display d-s">{t("The feeling", "Le ressenti")}</h3><p class="muted">{t("Living in it, staying in it, buying it", "Y vivre, y séjourner, l'acheter")}</p></div>
    </li>
    <li class="bw-wall" data-reveal>
      <span class="bw-block" aria-hidden="true"></span>
      <div><h3 class="display d-s">{t("First wall", "Premier mur")}</h3></div>
    </li>
  </ol>
  <p class="lede bw-note" data-reveal>{t("We make these decisions visible, while they can still change.", "Nous rendons ces décisions visibles, tant qu'elles peuvent encore changer.")}</p>
</section>

<section class="rail-wrap" data-rail>
  <div class="rail-head">
    <h2 class="display d-l" data-lines>{t("Selected work", "Projets choisis")}</h2>
    <a class="link" href="{url("projects.html")}">{t("All projects", "Tous les projets")}</a>
  </div>
  <div class="rail">{rail}</div>
</section>

<section class="hours">
  <div class="hours-copy">
    <span class="eyebrow" style="color:inherit">{t("Move across the image", "Déplacez-vous sur l'image")}</span>
    <h2 class="display d-l" style="max-width:10em;margin-top:10px">{t("Judge a building at every hour.", "Jugez un bâtiment à toute heure.")}</h2>
  </div>
  {compare_block(("estate-dusk", "estate-night", ("Sunset", "Coucher de soleil"), ("Night", "Nuit")), tease=True)}
</section>

<section class="lab-teaser" data-lab-teaser data-module="{PREFIX}js/lab.js" data-fallback="{img("tower-d4")}">
  <div class="sun-chip" aria-hidden="true"><i></i><b>09:00</b></div>
  <div class="lab-teaser-body">
    <div>
      <span class="eyebrow" style="color:var(--plaster)">{t("Plot Lab · This model is live", "Plot Lab · Ce modèle est en direct")}</span>
      <h2 class="display d-l" style="margin-top:10px">{t("Your plot, in 3D, in minutes.", "Votre terrain, en 3D, en quelques minutes.")}</h2>
    </div>
    <div>
      <p style="margin-bottom:18px">{t("Size a building on your plot, move the sun across the day, compare options and see a first budget. Then send the study straight to us.", "Dimensionnez un bâtiment sur votre terrain, déplacez le soleil, comparez des options et voyez un premier budget. Envoyez-nous ensuite votre étude.")}</p>
      {btn(t("Open the Plot Lab", "Ouvrir le Plot Lab"), url("plot-lab.html"))}
    </div>
  </div>
</section>

<section class="section wrap light">
  <div class="grid" style="margin-bottom:clamp(28px,4vw,60px);align-items:end">
    <h2 class="display d-l" style="grid-column:1/-1" data-lines>{t("What are you investing in?", "Dans quoi investissez-vous ?")}</h2>
  </div>
  <div class="types">{type_rows}</div>
</section>
<div class="float-img" aria-hidden="true">{float_imgs}</div>

{process_section()}
'''
    return layout("index.html", t("MMA Architects · Design the investment, not just the building", "MMA Architects · Concevez l'investissement, pas seulement le bâtiment"),
                  t("Architecture practice for people investing in Moroccan property: homes, apartment buildings, hotels and estates.", "Cabinet d'architecture pour celles et ceux qui investissent dans l'immobilier au Maroc."), main)


# ---------------------------------------------------------------- Projects index
def page_projects():
    cards = "".join(pcard(p) for p in PROJECTS)
    rows = "".join(
        f'<a href="{url("projects/" + p["slug"] + ".html")}" data-type="{p["type"]}" data-float="{p["slug"]}"><span class="display d-m">{escape(p_name(p))}</span><span class="muted">{escape(p_kind(p))}</span><span class="muted">{escape(p_place(p))}</span></a>'
        for p in PROJECTS)
    floats = "".join(f'<img src="{img(p["cover"])}" data-key="{p["slug"]}" alt="" loading="lazy">' for p in PROJECTS)
    chips = [("all", t("All", "Tous")), ("apartments", t("Apartments", "Appartements")), ("hospitality", t("Hospitality", "Hôtellerie")), ("villas", t("Villas", "Villas"))]
    chip_html = "".join(f'<button class="chip" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{escape(l)}</button>' for k, l in chips)
    main = f'''
<section class="page-head">
  <h1 class="display d-xl" data-lines>{t("Eight ways to read a plot.", "Huit façons de lire un terrain.")}</h1>
  <p class="lede" data-reveal>{t("From a single villa to 180 apartments. Each project starts with the same question: what can this site become, and what is it worth doing?", "De la villa aux 180 appartements. Chaque projet part de la même question : que peut devenir ce site, et que vaut-il la peine d'y faire ?")}</p>
</section>
<div class="pi-bar">
  <div class="chips" role="group" aria-label="{t("Filter by type", "Filtrer par type")}">{chip_html}</div>
  <div class="chips" role="group" aria-label="{t("View", "Affichage")}">
    <button class="chip" type="button" data-view="grid" aria-pressed="true">{t("Gallery", "Galerie")}</button>
    <button class="chip" type="button" data-view="list" aria-pressed="false">{t("Index", "Index")}</button>
  </div>
</div>
<div class="pi-grid">{cards}</div>
<div class="pi-list">{rows}</div>
<div class="float-img" aria-hidden="true">{floats}</div>
{final_cta("hotel-2")}
'''
    return layout("projects.html", t("Projects · MMA Architects", "Projets · MMA Architects"), t("Selected architecture projects by MMA in Morocco.", "Projets d'architecture de MMA au Maroc."), main, "projects")


# ---------------------------------------------------------------- Project page
def page_project(p, nxt):
    specs = ""
    for label, n, unit in p["specs"]:
        if n is None:
            value = pick(unit)
        else:
            value = f"{num(n)} {t(unit, unit)}" if unit else num(n)
        specs += f"<div><dt>{escape(pick(label))}</dt><dd>{escape(value)}</dd></div>"
    if not p["place"]:
        specs = f'<div><dt>{t("Location", "Lieu")}</dt><dd><span class="todo">{t("MMA to confirm", "À confirmer par MMA")}</span></dd></div>' + specs
    spec_block = f'<dl class="spec" data-reveal>{specs}</dl>' if specs else ""
    gal = "".join(f'<figure class="{cls}" data-reveal="img"><img src="{img(n)}" alt="{escape(p_name(p))}" loading="lazy"></figure>' for cls, n in p.get("gallery", []))
    gal_block = f'<section class="gal" style="padding-bottom:clamp(14px,2vw,28px)">{gal}</section>' if gal else ""
    cmp_block = ""
    if p.get("compare"):
        cmp_block = f'''<section style="padding-bottom:clamp(14px,2vw,28px)">
  <div class="wrap" style="padding-block:clamp(30px,5vw,70px) clamp(16px,2vw,26px)"><h2 class="display d-m">{t("See it at another hour.", "Voyez-le à une autre heure.")}</h2></div>
  {compare_block(p["compare"], "ph-compare", tease=True)}
</section>'''
    dia_block = ""
    if p.get("diagrams"):
        dia = "".join(f'<img src="{img(d)}" alt="" loading="lazy" data-reveal>' for d in p["diagrams"])
        dia_block = f'''<section class="light" style="padding-block:clamp(50px,7vw,110px)">
  <div class="wrap" style="margin-bottom:clamp(20px,3vw,44px)"><h2 class="display d-m" data-lines>{t("From the rules to the volume.", "Des règles au volume.")}</h2></div>
  <div class="diagrams">{dia}</div></section>'''
    plan_block = ""
    if p.get("plan"):
        plan_block = f'''<section class="light" style="padding-block:clamp(50px,7vw,110px)">
  <div class="wrap" style="margin-bottom:clamp(20px,3vw,44px)"><h2 class="display d-m" data-lines>{t("Read the plan up close.", "Lisez le plan de près.")}</h2><p class="muted" style="margin-top:8px">{t("Move over the drawing to magnify it.", "Survolez le dessin pour l'agrandir.")}</p></div>
  <div class="wrap"><div class="plan-wrap"><img src="{img(p["plan"])}" alt="{t("Floor plan", "Plan d'étage")}" loading="lazy"><div class="lens" aria-hidden="true"></div></div></div></section>'''
    type_map = {"apartments": "rental", "hospitality": "hospitality", "villas": "home"}
    main = f'''
<section class="ph-hero">
  <img src="{img(p["hero"])}" alt="{escape(p_name(p))}" style="view-transition-name:p-{p["slug"]}" fetchpriority="high">
  <div class="ph-hero-body">
    <span class="eyebrow" style="color:var(--plaster)">{escape(p_meta(p))}</span>
    <h1 class="display d-xl" data-lines>{escape(p_name(p))}</h1>
  </div>
</section>
<section class="section wrap white">
  <div class="ph-intro">
    <div>
      <h2 class="display d-l" data-lines>{escape(pick(p["pitch"]))}</h2>
      <p class="lede" style="margin-top:clamp(18px,2vw,30px)" data-reveal>{escape(pick(p["text"]))}</p>
      <div class="btn-row" style="margin-top:28px" data-reveal>{btn(t("A project like this?", "Un projet comme celui-ci ?"), url("contact.html") + "?type=" + type_map[p["type"]], "ink")}</div>
    </div>
    {spec_block}
  </div>
</section>
{dia_block}
{cmp_block}
{gal_block}
{plan_block}
<a class="next" href="{url("projects/" + nxt["slug"] + ".html")}" data-cursor="{t("Next", "Suivant")}">
  <img src="{img(nxt["cover"])}" alt="" loading="lazy" style="view-transition-name:p-{nxt["slug"]}">
  <div class="next-body"><span class="eyebrow" style="color:var(--plaster)">{t("Next project", "Projet suivant")}</span><p class="display d-xl" style="margin-top:12px">{escape(p_name(nxt))}</p></div>
</a>
'''
    return layout(f'projects/{p["slug"]}.html', f"{p_name(p)} · MMA Architects", pick(p["text"]), main, "projects")


# ---------------------------------------------------------------- Plot Lab
def page_lab():
    programs = [("villa", t("Villa", "Villa")), ("apartments", t("Apartments", "Appartements")), ("hotel", t("Hotel", "Hôtel"))]
    finishes = [("standard", t("Standard", "Standard")), ("premium", t("Premium", "Premium")), ("highend", t("High-end", "Haut de gamme"))]
    prog = "".join(f'<button type="button" data-program="{k}">{escape(l)}</button>' for k, l in programs)
    fin = "".join(f'<button type="button" data-finish="{k}">{escape(l)}</button>' for k, l in finishes)
    i18n = {"lab": {
        "rates": {"standard": [5500, 7500], "premium": [8000, 12000], "highend": [12500, 18000]},
        "ground": t("G", "R"), "units": t("apartments", "appartements"), "rooms": t("rooms", "chambres"), "oneVilla": t("1 villa", "1 villa"),
        "play": t("Play the day", "Lancer la journée"), "pause": t("Pause", "Pause"),
        "share": t("Copy link", "Copier le lien"), "copied": t("Link copied", "Lien copié"), "linkInBar": t("Link is in the address bar", "Lien dans la barre d'adresse"),
        "save": t("Save option", "Garder l'option"), "saved": t("Saved", "Gardée"),
        "option": t("Option", "Option"), "remove": t("Remove", "Retirer"),
        "programs": dict(programs), "finishes": dict(finishes), "contactUrl": url("contact.html"),
        "locale": LOCALES[LANG], "dateLocale": {"ar": "ar-MA", "zh": "zh-CN"}.get(LANG, LOCALES[LANG]), "m2": t("m²", "m²"), "mad": t("MAD", "MAD"),
        "plotSample": t("Sample plot, Tangier", "Terrain d'exemple, Tanger"),
        "plotSampleNote": t("The sun is real for Tangier. The square plot, road and neighbours are only illustrative.", "Le soleil est réel pour Tanger. Le terrain carré, la route et les voisins sont seulement illustratifs."),
        "plotYours": t("Your plot", "Votre terrain"),
        "plotPick": t("Select my plot on a map", "Choisir mon terrain sur une carte"), "plotChange": t("Change the plot", "Modifier le terrain"),
        "studyPlot": t("Plot", "Terrain"),
        "fitLimit": t("The shape of this plot limits a rectangular building to about {pct} % coverage. The figures use that.", "La forme de ce terrain limite un bâtiment rectangulaire à environ {pct} % d'emprise. Les chiffres en tiennent compte."),
        "sunrise": t("Sunrise", "Lever"), "sunset": t("Sunset", "Coucher"),
        "noRiseSet": t("No sunrise or sunset on this date", "Ni lever ni coucher du soleil à cette date"),
        "sunNow": t("Sun {alt}° above the horizon, {az}° from north", "Soleil à {alt}° au-dessus de l'horizon, {az}° depuis le nord"),
        "sunBelow": t("The sun is below the horizon", "Le soleil est sous l'horizon"),
        "map": {
            "imagery": IMAGERY_URL, "imageryCredit": IMAGERY_CREDIT, "street": STREET_URL, "streetCredit": STREET_CREDIT,
            "drawHint": t("Find your plot, then click each of its corners.", "Trouvez votre terrain, puis cliquez sur chacun de ses angles."),
            "moreCorners": t("Keep going: a plot needs at least 3 corners.", "Continuez : il faut au moins 3 angles."),
            "zoomIn": t("Zooming in. Click again to place the corner accurately.", "Zoom en cours. Cliquez de nouveau pour placer l'angle avec précision."),
            "measured": t("Measured area: about {area} m². Drag a corner to adjust it.", "Surface mesurée : environ {area} m². Faites glisser un angle pour l'ajuster."),
            "crossing": t("The sides of the plot cross. Move a corner or undo the last one.", "Les côtés du terrain se croisent. Déplacez un angle ou annulez le dernier."),
            "tooSmall": t("This is smaller than {n} m². Check the corners.", "C'est moins de {n} m². Vérifiez les angles."),
            "tooLarge": t("This is larger than {n} m², the most the Plot Lab can study.", "C'est plus de {n} m², le maximum que le Plot Lab peut étudier."),
            "searchNone": t("Nothing found. Try a nearby town or paste coordinates.", "Aucun résultat. Essayez une ville proche ou collez des coordonnées."),
            "searchFail": t("The search isn't responding. Try moving the map by hand.", "La recherche ne répond pas. Essayez de déplacer la carte à la main."),
            "gpsFail": t("Your location isn't available. Check the browser's permission or search instead.", "Votre position n'est pas disponible. Vérifiez l'autorisation du navigateur ou lancez une recherche."),
            "loadFail": t("The map couldn't load. Check your connection and try again.", "La carte n'a pas pu se charger. Vérifiez votre connexion et réessayez."),
        },
        "noGl": t("3D isn't available in this browser. You can still use the controls to see the figures.", "La 3D n'est pas disponible dans ce navigateur. Les réglages restent utilisables pour voir les chiffres."),
    }}
    send_attrs = ""
    if LANG == "zh":
        # No Chinese contact form: the study goes by WhatsApp, worded so that the French, English and Arabic speaking team can read it.
        i18n["lab"].update({
            "levelsText": "{n} 层", "ground": "G", "studyPlot": "Plot",
            "send": {"whatsapp": PHONES[0][1], "intro": "您好 MMA，这是我的地块研究。/ Hello MMA, here is my Plot Lab study.",
                     "programs": {"villa": "别墅 / Villa", "apartments": "公寓 / Apartments", "hotel": "酒店 / Hotel"}},
        })
        send_attrs = ' target="_blank" rel="noopener"'
    th = "".join(f"<th scope=col>{escape(x)}</th>" for x in [t("Option", "Option"), t("Type", "Type"), t("Plot", "Terrain"), t("Coverage", "Emprise"), t("Levels", "Niveaux"), t("Floor area", "Surface"), t("Capacity", "Capacité"), t("Finish", "Finition"), t("Budget (MAD)", "Budget (MAD)"), ""])
    main = f'''
<section class="lab" id="labRoot">
  <div class="lab-stage">
    <div class="lab-canvas" aria-label="{t("3D model of the building on the plot. Drag to turn it.", "Modèle 3D du bâtiment sur le terrain. Faites glisser pour le tourner.")}"></div>
    <div class="lab-title">
      <h1 class="display d-l" data-lines>{t("Plot Lab", "Plot Lab")}</h1>
      <p style="margin-top:6px;max-width:27em">{t("Shape a first idea of your project, then send it to the architects.", "Dessinez une première idée de votre projet, puis envoyez-la aux architectes.")}</p>
    </div>
    <div class="lab-compass" role="img" aria-label="{t("Compass showing north", "Boussole indiquant le nord")}"><i aria-hidden="true"><b>N</b></i></div>
    <p class="lab-hint">{t("Drag to turn · Scroll or pinch to zoom", "Glissez pour tourner · Molette ou pincement pour zoomer")}</p>
    <p class="lab-credit hide">{IMAGERY_CREDIT}</p>
  </div>
  <aside class="lab-panel" data-lenis-prevent aria-label="{t("Study controls", "Réglages de l'étude")}">
    <div class="lab-plot">
      <strong id="plotLabel"></strong>
      <span id="plotDetail"></span>
      <div class="lab-plot-actions"><button class="mini" id="plotPick" type="button"></button><button class="link" id="plotReset" type="button">{t("Back to the sample", "Revenir à l'exemple")}</button></div>
    </div>
    <div class="seg" role="group" aria-label="{t("Type of project", "Type de projet")}">{prog}</div>
    <div class="ctl" id="labAreaCtl"><label for="labArea"><span>{t("Plot size", "Surface du terrain")}</span><output id="outArea"></output></label><input id="labArea" type="range" step="50"></div>
    <div class="ctl"><label for="labCover"><span>{t("Coverage of the plot", "Emprise au sol")}</span><output id="outCover"></output></label><input id="labCover" type="range" step="5"><p class="note lab-fit hide" id="labFitNote" role="status"></p></div>
    <div class="ctl"><label for="labFloors"><span>{t("Levels", "Niveaux")}</span><output id="outFloors"></output></label><input id="labFloors" type="range" step="1"></div>
    <div class="ctl"><label for="labDay"><span>{t("Date", "Date")}</span><output id="outDay"></output></label><input id="labDay" type="range" min="1" max="366" step="1"><div class="day-shortcuts"><button type="button" data-day="today">{t("Today", "Aujourd'hui")}</button><button type="button" data-day="june"></button><button type="button" data-day="december"></button></div></div>
    <div class="ctl"><label for="labHour"><span>{t("Time at the plot", "Heure sur le terrain")}</span><output id="outHour"></output></label><input id="labHour" type="range" min="0" max="24" step="0.25"><button class="link" id="labPlay" type="button" style="font-size:13px;margin-top:3px">{t("Play the day", "Lancer la journée")}</button>
      <p class="sun-facts"><span id="outSunTimes"></span><span id="outSunNow"></span></p></div>
    <div class="seg" role="group" aria-label="{t("Level of finish", "Niveau de finition")}">{fin}</div>
    <p class="note">{t("Illustrative only, using sample rates that MMA will confirm. Real limits come from your plot's planning rules, and the plot you draw is not a survey. Capacity assumes 85 m² per apartment and 40 m² per room. The sun's position is calculated for the place and date. The ground is shown flat, with a clear sky, and without shade from neighbouring buildings or hills.",
      "À titre indicatif, avec des tarifs d'exemple que MMA confirmera. Les limites réelles dépendent des règles d'urbanisme de votre terrain, et le tracé que vous dessinez ne remplace pas un relevé. Capacité sur la base de 85 m² par appartement et 40 m² par chambre. La position du soleil est calculée pour le lieu et la date. Le sol est représenté plat, par ciel dégagé, sans l'ombre des bâtiments voisins ni des reliefs.")}</p>
    <div class="lab-sticky">
    <div class="lab-res" aria-live="polite">
      <div><span>{t("Floor area", "Surface de plancher")}</span><strong id="resFloor"></strong></div>
      <div><span>{t("Rough capacity", "Capacité estimée")}</span><strong id="resCap"></strong></div>
      <div class="wide"><span>{t("First budget, excluding land", "Premier budget, hors terrain")}</span><strong id="resBudget"></strong></div>
    </div>
    <div class="lab-actions">
      <a class="btn" id="labSend" href="{url("contact.html")}"{send_attrs}>{t("Send this study to MMA", "Envoyer cette étude à MMA")} {ARROW}</a>
      <button class="mini" id="labSave" type="button">{t("Save option", "Garder l'option")}</button>
      <button class="mini" id="labShare" type="button">{t("Copy link", "Copier le lien")}</button>
    </div>
    </div>
  </aside>
</section>
<dialog class="plot-dialog" id="plotDialog" data-lenis-prevent aria-labelledby="plotDialogTitle">
  <div class="plot-head">
    <h2 class="display d-s" id="plotDialogTitle">{t("Find your plot", "Trouvez votre terrain")}</h2>
    <form id="plotSearch" role="search">
      <input id="plotQuery" type="search" autocomplete="off" aria-label="{t("Address, place or coordinates", "Adresse, lieu ou coordonnées")}" placeholder="{t("Address, place or coordinates", "Adresse, lieu ou coordonnées")}">
      <button class="mini" type="submit">{t("Search", "Rechercher")}</button>
    </form>
    <button class="mini" id="plotGps" type="button">{t("Use my location", "Ma position")}</button>
    <div class="seg" role="group" aria-label="{t("Map type", "Type de carte")}"><button type="button" data-layer="satellite" aria-pressed="true">{t("Satellite", "Satellite")}</button><button type="button" data-layer="street" aria-pressed="false">{t("Streets", "Rues")}</button></div>
  </div>
  <div class="plot-results" id="plotResults"></div>
  <div class="plot-map-wrap"><div id="plotMap" dir="ltr"></div><span class="plot-cross" aria-hidden="true"></span></div>
  <div class="plot-foot">
    <p id="plotStatus" role="status"></p>
    <div class="plot-tools">
      <button class="mini" id="plotAddCentre" type="button">{t("Add a corner at the crosshair", "Ajouter un angle au viseur")}</button>
      <button class="mini" id="plotUndo" type="button">{t("Undo", "Annuler")}</button>
      <button class="mini" id="plotClear" type="button">{t("Clear", "Effacer")}</button>
      <button class="mini" id="plotCancel" type="button">{t("Cancel", "Fermer")}</button>
      <button class="btn" id="plotUse" type="button" disabled>{t("Use this plot", "Utiliser ce terrain")} {ARROW}</button>
    </div>
    <p class="note">{t("Searches go to OpenStreetMap and map views to the map providers. MMA only receives your plot if you send the study.", "Les recherches passent par OpenStreetMap et l'affichage de la carte par ses fournisseurs. MMA ne reçoit votre terrain que si vous envoyez l'étude.")}</p>
  </div>
</dialog>
<section class="section wrap white hide" id="labCompare" style="padding-block:clamp(40px,6vw,90px)">
  <h2 class="display d-m" style="margin-bottom:22px">{t("Your options, side by side.", "Vos options, côte à côte.")}</h2>
  <div class="table-scroll"><table class="compare-table"><thead><tr>{th}</tr></thead><tbody id="labCompareBody"></tbody></table></div>
</section>
{final_cta("tower-3")}
'''
    js = f"<script type=\"module\">import {{mountLab}} from '{PREFIX}js/lab.js';mountLab(document.getElementById('labRoot'));</script>"
    return layout("plot-lab.html", t("Plot Lab · MMA Architects", "Plot Lab · MMA Architects"), t("Test your plot in 3D: massing, sun, floor area and a first budget.", "Testez votre terrain en 3D : volume, soleil, surface et premier budget."), main, "lab", extra_js=js, i18n=i18n)


# ---------------------------------------------------------------- Expertise
def page_expertise():
    stage_html = "".join(f'<article class="stage"><b>{n + 1}</b><h3>{escape(a)}</h3><p>{escape(b)}</p></article>' for n, (a, b, *_) in enumerate(stages()))
    details = {
        "home": [t("Designs that fit the plot and how you live", "Un projet adapté au terrain et à votre façon de vivre"), t("Views, shade, privacy and orientation resolved early", "Vues, ombre, intimité et orientation réglées tôt"), t("Pools, gardens and terraces drawn as one composition", "Piscines, jardins et terrasses dessinés d'un seul geste")],
        "rental": [t("Unit mix tested against what the rules allow", "Typologies testées face à ce que les règles permettent"), t("Plans drawn for easy sale or rental", "Des plans pensés pour la vente ou la location"), t("Parking, circulation and shared spaces that hold up", "Parking, circulations et parties communes qui tiennent")],
        "hospitality": [t("Rooms, circulation and services balanced from the start", "Chambres, circulations et services équilibrés dès le départ"), t("Arrival, lobby and room design as one experience", "Arrivée, hall et chambres pensés comme une seule expérience"), t("Design that uses the site's view as its main asset", "Un projet qui fait de la vue son premier atout")],
        "estate": [t("Master plan across several buildings", "Plan d'ensemble sur plusieurs bâtiments"), t("Privacy between homes on a shared site", "Intimité entre les maisons sur un site partagé"), t("Shared gardens, event and guest spaces", "Jardins communs, espaces d'accueil et de réception")],
        "interior": [t("Layouts that make the most of every room", "Des aménagements qui tirent parti de chaque pièce"), t("Materials, finishes and lighting chosen together", "Matériaux, finitions et éclairage choisis ensemble"), t("Furniture and joinery designed for the space", "Mobilier et menuiseries pensés pour le lieu")],
    }
    items = ""
    for key, im, title, q, slug in TYPES:
        checks = "".join(f"<li>{escape(c)}</li>" for c in details[key])
        items += f'''<article class="invest-item" id="{key}">
  <div class="ii-img" data-reveal="img"><img src="{img(im)}" alt="" loading="lazy"></div>
  <div>
    <h3 class="display d-m">{escape(pick(title))}</h3>
    <p class="muted" style="margin-top:10px">{escape(pick(q))}</p>
    <ul class="checks">{checks}</ul>
    <div class="btn-row" style="margin-top:20px">{btn(t("Discuss this project", "Parler de ce projet"), url("contact.html") + "?type=" + key, "ink")}<a class="link" style="align-self:center" href="{url("projects/" + slug + ".html")}">{t("See an example", "Voir un exemple")}</a></div>
  </div>
</article>'''
    main = f'''
<section class="page-head">
  <h1 class="display d-xl" data-lines>{t("Architecture that answers an investor's questions.", "Une architecture qui répond aux questions de l'investisseur.")}</h1>
  <p class="lede" data-reveal>{t("You can start with a feasibility study alone, then decide. You approve each stage before the next begins.", "Vous pouvez commencer par la seule étude de faisabilité, puis décider. Vous validez chaque étape avant la suivante.")}</p>
</section>
<section class="stages-pin">
  <div class="wrap"><h2 class="display d-m">{t("Six stages, one team.", "Six étapes, une seule équipe.")}</h2></div>
  <div class="stages-track">{stage_html}</div>
</section>
<section class="section wrap light" style="padding-bottom:0">
  <h2 class="display d-l" data-lines style="margin-bottom:clamp(28px,4vw,60px)">{t("What we design", "Ce que nous concevons")}</h2>
  <div>{items}</div>
</section>
<section class="section wrap">
  <span class="eyebrow">{t("From the portfolio", "Dans le portfolio")}</span>
  <div class="facts" style="margin-top:22px">
    <div class="fact"><strong data-count="27024" data-locale="{LOCALES[LANG]}" data-unit=" {t("m²", "m²")}">{num(27024)} {t("m²", "m²")}</strong><span>{t("floor area on the largest scheme", "de plancher sur le plus grand projet")}</span></div>
    <div class="fact"><strong data-count="180" data-locale="en-GB">180</strong><span>{t("apartments in one building", "appartements dans un immeuble")}</span></div>
    <div class="fact"><strong data-count="6250" data-locale="{LOCALES[LANG]}" data-unit=" {t("m²", "m²")}">{num(6250)} {t("m²", "m²")}</strong><span>{t("4-star hotel in Chefchaouen", "hôtel 4 étoiles à Chefchaouen")}</span></div>
    <div class="fact"><strong data-count="8" data-locale="en-GB">8</strong><span>{t("projects in the selected works", "projets dans la sélection")}</span></div>
  </div>
</section>
{final_cta("resort-1")}
'''
    return layout("expertise.html", t("Expertise · MMA Architects", "Expertise · MMA Architects"), t("Feasibility, design, permits and supervision for property investors in Morocco.", "Faisabilité, conception, permis et suivi pour les investisseurs immobiliers au Maroc."), main, "expertise")


# ---------------------------------------------------------------- Studio
def page_studio():
    main = f'''
<section class="page-head">
  <h1 class="display d-xl" data-lines>{t("Two architects. One signature.", "Deux architectes. Une signature.")}</h1>
  <p class="lede" data-reveal>{t("MMA is the partnership of two architects, Mharrech and Mribah. When you work with us, you deal directly with the people designing your project.", "MMA est l'association de deux architectes, Mharrech et Mribah. Avec nous, vous échangez directement avec les personnes qui conçoivent votre projet.")}</p>
</section>
<section class="wrap" style="padding-bottom:clamp(60px,8vw,120px)">
  <div class="partners">
    <article class="partner" data-reveal="img"><img src="{img("partner-mharrech")}" alt="" loading="lazy"><div class="partner-body"><span class="eyebrow" style="color:inherit">{t("Architect, partner", "Architecte, associé")}</span><h2 class="display d-m" style="margin-top:6px">Mharrech</h2></div></article>
    <article class="partner" data-reveal="img"><img src="{img("partner-mribah")}" alt="" loading="lazy"><div class="partner-body"><span class="eyebrow" style="color:inherit">{t("Architect, partner", "Architecte, associé")}</span><h2 class="display d-m" style="margin-top:6px">Mribah</h2></div></article>
  </div>
</section>
<section class="section wrap light">
  <h2 class="display d-l" data-lines style="margin-bottom:clamp(30px,5vw,70px);max-width:13em">{t("Why investors work with architects first.", "Pourquoi commencer par l'architecte.")}</h2>
  <div class="values">
    <div><h3 class="display d-s">{t("We start with the plot", "Le terrain d'abord")}</h3><p class="muted">{t("A site's real potential sits in its planning rules, shape and context. We read those first, because they set everything that follows.", "Le vrai potentiel d'un site tient à ses règles, sa forme et son contexte. Nous les lisons d'abord, car ils décident de tout le reste.")}</p></div>
    <div><h3 class="display d-s">{t("We make it visible", "Rendre visible")}</h3><p class="muted">{t("3D studies, day and night views and clear plans mean you can judge a decision before it costs anything to change.", "Études 3D, vues de jour et de nuit, plans clairs : vous jugez une décision avant qu'elle ne coûte à changer.")}</p></div>
    <div><h3 class="display d-s">{t("We stay on your side", "De votre côté")}</h3><p class="muted">{t("From the first study to handover, your architect's job is to represent the project you decided on.", "De la première étude à la réception, le rôle de votre architecte est de défendre le projet que vous avez décidé.")}</p></div>
  </div>
</section>
{final_cta("estate-2")}
'''
    return layout("studio.html", t("Studio · MMA Architects", "Studio · MMA Architects"), t("MMA is the partnership of architects Mharrech and Mribah.", "MMA est l'association des architectes Mharrech et Mribah."), main, "studio")


# ---------------------------------------------------------------- Contact: the project brief
def page_contact():
    types = [("home", t("A villa or home", "Une villa ou une maison"), t("For you, your family or to resell", "Pour vous, votre famille ou la revente")),
             ("rental", t("An apartment building", "Un immeuble d'appartements"), t("To rent or to sell", "À louer ou à vendre")),
             ("hospitality", t("A hotel or guest house", "Un hôtel ou une maison d'hôtes"), t("From a riad to a resort", "Du riad au complexe")),
             ("estate", t("A multi-building estate", "Un domaine de plusieurs bâtiments"), t("Villas, guest spaces, shared gardens", "Villas, accueil, jardins communs")),
             ("interior", t("Interior design", "L'architecture d'intérieur"), t("For a home, a hotel or a rental", "Pour une maison, un hôtel ou une location")),
             ("other", t("Something else", "Autre chose"), t("Offices, retail, renovation...", "Bureaux, commerces, rénovation...")),]
    stages = [("plot", t("I have a plot", "J'ai un terrain"), t("And I want to know what it can become", "Et je veux savoir ce qu'il peut devenir")),
              ("looking", t("I'm looking for one", "Je cherche un terrain"), t("And I want advice before buying", "Et je veux un avis avant d'acheter")),
              ("building", t("I have a building", "J'ai un bâtiment"), t("And I want to transform it", "Et je veux le transformer"))]
    budgets = [("b1", t("Under 2M MAD", "Moins de 2 M MAD"), ""), ("b2", t("2–5M MAD", "2 à 5 M MAD"), ""), ("b3", t("5–20M MAD", "5 à 20 M MAD"), ""), ("b4", t("Over 20M MAD", "Plus de 20 M MAD"), ""), ("b0", t("Not sure yet", "Pas encore défini"), "")]

    def opts(field, items):
        return '<div class="opts">' + "".join(
            f'<button class="opt" type="button" data-field="{field}" data-value="{k}"><strong>{escape(a)}</strong>{f"<small>{escape(b)}</small>" if b else ""}</button>' for k, a, b in items) + "</div>"

    matches = {}
    for key, _, _, _, slug in TYPES:
        p = by_slug(slug)
        matches[key] = {"name": p_name(p), "img": img(p["cover"]), "url": url("projects/" + slug + ".html")}
    i18n = {
        "errType": t("Choose a type of project to continue.", "Choisissez un type de projet pour continuer."),
        "errStage": t("Tell us where you are to continue.", "Indiquez où vous en êtes pour continuer."),
        "errContact": t("Add your name and phone number so we can reply.", "Ajoutez votre nom et votre téléphone pour que nous puissions répondre."),
        "sType": t("Project", "Projet"), "sStage": t("Status", "Situation"), "sCity": t("City", "Ville"), "sBudget": t("Budget", "Budget"),
        "sStudy": t("Plot Lab study", "Étude Plot Lab"), "sName": t("Name", "Nom"), "sPhone": t("Phone", "Téléphone"), "sMsg": t("Notes", "Notes"),
        "waIntro": t("Hello MMA, here is my project:", "Bonjour MMA, voici mon projet :"), "matches": matches,
    }
    side = f'<img src="{img("hotel-3")}" data-key="default" class="on" alt="">' + "".join(f'<img src="{img(im)}" data-key="{key}" alt="" loading="lazy">' for key, im, *_ in TYPES)
    main = f'''
<section class="brief">
  <div class="brief-side" aria-hidden="true">{side}</div>
  <form class="brief-main" id="brief" novalidate>
    <div class="brief-bar" aria-hidden="true"><i></i></div>
    <div class="step"><span class="eyebrow">{t("Your project · 1 of 5", "Votre projet · 1 sur 5")}</span><h1 class="display d-l">{t("What do you want to create?", "Que voulez-vous créer ?")}</h1>{opts("type", types)}</div>
    <div class="step"><span class="eyebrow">{t("Your project · 2 of 5", "Votre projet · 2 sur 5")}</span><h2 class="display d-l">{t("Where are you today?", "Où en êtes-vous aujourd'hui ?")}</h2>{opts("stage", stages)}</div>
    <div class="step"><span class="eyebrow">{t("Your project · 3 of 5", "Votre projet · 3 sur 5")}</span><h2 class="display d-l">{t("Roughly what budget?", "Quel budget, à peu près ?")}</h2>{opts("budget", budgets)}</div>
    <div class="step"><span class="eyebrow">{t("Your project · 4 of 5", "Votre projet · 4 sur 5")}</span><h2 class="display d-l">{t("How can we reach you?", "Comment vous joindre ?")}</h2>
      <div class="fields-2">
        <label class="field"><span>{t("Your name", "Votre nom")}</span><input id="fName" type="text" autocomplete="name" required></label>
        <label class="field"><span>{t("Phone or WhatsApp", "Téléphone ou WhatsApp")}</span><input id="fPhone" type="tel" autocomplete="tel" required></label>
        <label class="field"><span>{t("City of the project (optional)", "Ville du projet (facultatif)")}</span><input id="fCity" type="text"></label>
      </div>
      <label class="field"><span>{t("Anything else? (optional)", "Autre chose ? (facultatif)")}</span><textarea id="fMsg"></textarea></label>
    </div>
    <div class="step"><span class="eyebrow">{t("Your project · 5 of 5", "Votre projet · 5 sur 5")}</span><h2 class="display d-m">{t("Your brief is ready.", "Votre brief est prêt.")}</h2>
      <dl class="summary" id="summary"></dl>
      <a class="match hide" id="match" href="#"><img src="" alt=""><span><span class="eyebrow">{t("Closest project", "Projet le plus proche")}</span><strong style="display:block;font-weight:500"></strong></span></a>
      <div class="btn-row">
        <a class="btn" data-wa="{PHONES[0][1]}" href="https://wa.me/{PHONES[0][1]}" target="_blank" rel="noopener">{t("Send on WhatsApp", "Envoyer sur WhatsApp")} {ARROW}</a>
        <a class="btn ghost" href="tel:+{PHONES[0][1]}">{t("Call", "Appeler")} {phone_text(0)}</a>
      </div>
      <p class="note" style="margin-top:14px">{t("WhatsApp opens with your brief written out, so you can review it before you send it.", "WhatsApp s'ouvre avec votre brief rédigé, pour que vous le relisiez avant de l'envoyer.")}</p>
    </div>
    <p class="brief-err" role="alert"></p>
    <div class="brief-nav">
      <button class="link" id="briefBack" type="button">{t("Back", "Retour")}</button>
      <div><button class="btn" id="briefNext" type="button">{t("Continue", "Continuer")} {ARROW}</button></div>
    </div>
  </form>
</section>
'''
    return layout("contact.html", t("Start a project · MMA Architects", "Lancer un projet · MMA Architects"), t("Tell MMA about your project in under a minute.", "Présentez votre projet à MMA en moins d'une minute."), main, "", i18n=i18n)


# ---------------------------------------------------------------- Chinese landing page
def page_zh():
    """One focused page for Chinese companies in Morocco. Apart from the Plot Lab, the full site is not translated into Chinese."""
    services = [
        ("apartments-day", "员工住宅与管理层公寓", "为派驻摩洛哥的团队规划住宿：在规划条例允许的范围内，测算可建户数、户型与停车位。我们设计过一栋 180 户、总建筑面积 27,024 m² 的住宅楼。"),
        ("tower-3", "办公与配套建筑", "为您在丹吉尔、卡萨布兰卡等城市的机构设计办公及配套空间，在动工之前把功能、动线与预算确定下来。"),
        ("hotel-dusk", "酒店与商务接待", "统筹客房、动线与服务空间。我们设计过舍夫沙万一座总建筑面积 6,250 m² 的四星级酒店。"),
    ]
    service_html = "".join(
        f'<article class="invest-item"><div class="ii-img" data-reveal="img"><img src="{img(im)}" alt="" loading="lazy"></div><div><h3 class="display d-m">{title}</h3><p class="muted" style="margin-top:10px">{body}</p></div></article>'
        for im, title, body in services)
    works = [("180-apartments-tangier", "180 户住宅楼", "丹吉尔 · 住宅"), ("residential-tower-tangier", "住宅塔楼", "丹吉尔 · 住宅"),
             ("hotel-chefchaouen", "四星级酒店", "舍夫沙万 · 酒店"), ("suites-tower", "套房塔楼", "酒店")]
    work_html = "".join(
        f'<article class="pcard"><div class="pcard-media"><img src="{img(by_slug(s)["cover"])}" alt="{name}" loading="lazy"></div><div class="pcard-info"><h3>{name}</h3><span>{meta}</span></div></article>'
        for s, name, meta in works)
    steps = [("可行性研究", "研读规划条例，测试地块的实际承载能力，然后再决定下一步。"), ("方案设计", "提供平面、体量与三维视图，便于比较和反馈。"),
             ("扩初设计", "深化选定方案，协调平面、剖面、立面与材料。"), ("建筑许可", "准备并提交申请，并与主管部门跟进。"),
             ("承包商比选", "提供施工文件和可比报价，并给出明确建议。"), ("工地监理", "定期巡视并提交报告，直至交付。")]
    step_html = "".join(f'<article class="stage"><b>{n}</b><h3>{a}</h3><p>{b}</p></article>' for n, (a, b) in enumerate(steps, 1))
    wa = wa_link(t("Hello MMA, I would like to talk about a project.", ""))
    main = f"""
<section class="ph-hero">
  <img src="{img("apartments-dusk")}" alt="丹吉尔 180 户住宅楼效果图" fetchpriority="high">
  <div class="ph-hero-body">
    <span class="eyebrow" style="color:var(--plaster)">摩洛哥丹吉尔 · 建筑设计事务所</span>
    <h1 class="display d-xl" data-lines>在摩洛哥建设，先读懂土地。</h1>
    <p class="lede" style="margin-top:18px" data-reveal>MMA 为在摩洛哥投资建设的企业提供建筑设计服务，从可行性研究、建筑许可到工地监理，由同一支团队全程负责。</p>
    <div class="btn-row" style="margin-top:22px" data-reveal>{btn("咨询项目", "#contact")}{btn("查看项目案例", "#work", "ghost")}</div>
  </div>
</section>
<section class="section wrap light zh-anchor" id="services">
  <h2 class="display d-l" data-lines style="margin-bottom:clamp(28px,4vw,60px)">我们能为您的团队设计什么</h2>
  <div>{service_html}</div>
</section>
<section class="section wrap zh-anchor" id="work">
  <h2 class="display d-l" data-lines style="margin-bottom:clamp(28px,4vw,60px)">项目案例</h2>
  <div class="pi-grid zh-works">{work_html}</div>
  <div class="facts" style="margin-top:clamp(40px,6vw,80px)">
    <div class="fact"><strong>27,024 m²</strong><span>最大项目的总建筑面积</span></div>
    <div class="fact"><strong>180</strong><span>单栋住宅楼的户数</span></div>
    <div class="fact"><strong>6,250 m²</strong><span>舍夫沙万四星级酒店</span></div>
    <div class="fact"><strong>8</strong><span>精选项目</span></div>
  </div>
</section>
<section class="section wrap zh-anchor" id="process" style="padding-top:0">
  <h2 class="display d-l" data-lines style="margin-bottom:clamp(28px,4vw,60px)">六个阶段，一支团队</h2>
  <div class="zh-stages">{step_html}</div>
  <p class="lede" style="margin-top:clamp(24px,3vw,44px)" data-reveal>每个阶段经您确认后才进入下一阶段。您也可以只委托可行性研究，然后再做决定。</p>
</section>
<section class="final zh-anchor" id="contact">
  <img src="{img("tower-3")}" alt="" loading="lazy" data-parallax="5">
  <div class="final-body">
    <h2 class="display d-l" data-lines>告诉我们您的地块和项目需求。</h2>
    <div class="btn-row" data-reveal><a class="btn" href="{wa}" target="_blank" rel="noopener">通过 WhatsApp 联系 {ARROW}</a><a class="btn ghost" href="tel:+{PHONES[0][1]}">致电 {phone_text(0)}</a></div>
    <p class="lede" style="margin-top:22px" data-reveal>我们目前使用法语、英语和阿拉伯语沟通，欢迎您的本地代表或翻译一同参与。</p>
    <p style="margin-top:14px" data-reveal><a class="link" href="{PREFIX}en/projects.html">查看全部项目（英文）</a></p>
  </div>
</section>
"""
    return layout("index.html", "MMA Architects · 摩洛哥建筑设计事务所", "MMA 是位于摩洛哥丹吉尔的建筑设计事务所，为在摩洛哥投资建设的企业提供从可行性研究到工地监理的服务。", main)


# ---------------------------------------------------------------- Build
def write(rel, html):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def build():
    global LANG, PREFIX, ZH_LANDING
    count = 0
    for LANG in ("en", "fr", "es", "ar"):
        PREFIX = "../"
        for name, fn in (("index", page_home), ("projects", page_projects), ("plot-lab", page_lab), ("expertise", page_expertise), ("studio", page_studio), ("contact", page_contact)):
            write(f"{LANG}/{name}.html", fn())
            count += 1
        PREFIX = "../../"
        for i, p in enumerate(PROJECTS):
            write(f'{LANG}/projects/{p["slug"]}.html', page_project(p, PROJECTS[(i + 1) % len(PROJECTS)]))
            count += 1
    LANG, PREFIX = "zh", "../"
    ZH_LANDING = True
    write("zh/index.html", page_zh())
    ZH_LANDING = False
    write("zh/plot-lab.html", page_lab())
    count += 2
    if MISSING:
        raise SystemExit("Missing translations (add them to translations.py):\n" + "\n".join(f"  [{l}] {s}" for l, s in sorted(MISSING)))
    write("index.html", '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>MMA Architects</title>
<meta http-equiv="refresh" content="0;url=fr/index.html">
<script>location.replace('fr/index.html')</script>
</head><body><a href="fr/index.html">Français</a> · <a href="en/index.html">English</a> · <a href="es/index.html">Español</a> · <a href="ar/index.html" dir="rtl">العربية</a> · <a href="zh/index.html">中文</a></body></html>
''')
    write("404.html", '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable · MMA Architects</title><meta name="robots" content="noindex">
<style>body{margin:0;min-height:100svh;display:grid;place-content:center;gap:14px;padding:24px;background:#0B1A1F;color:#EFEDE8;font:400 18px/1.5 system-ui,sans-serif}img{width:150px;height:auto}a{color:#F0A35E}</style>
</head><body><img src="/assets/logo-mma-white.png" alt="MMA, Mharrech Mribah Architects">
<p>Cette page n'existe pas. <a href="/fr/index.html">Retour à l'accueil</a></p>
<p>This page doesn't exist. <a href="/en/index.html">Back to home</a></p>
<p>Esta página no existe. <a href="/es/index.html">Volver al inicio</a></p>
<p dir="rtl">هذه الصفحة غير موجودة. <a href="/ar/index.html">العودة إلى الرئيسية</a></p>
<p>页面不存在。<a href="/zh/index.html">返回首页</a></p>
</body></html>
''')
    print(f"Built {count} pages")


if __name__ == "__main__":
    build()
