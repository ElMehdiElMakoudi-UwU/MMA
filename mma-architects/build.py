#!/usr/bin/env python3
"""Generates the MMA Architects site in French and English. Run: python3 build.py"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PHONES = [("06 61 22 50 67", "212661225067"), ("06 33 93 15 42", "212633931542")]
LANG = "en"
PREFIX = ""
OTHER_PATH = ""


def t(en, fr):
    return fr if LANG == "fr" else en


def num(n):
    s = f"{n:,}"
    return s.replace(",", " ") if LANG == "fr" else s


def img(name):
    return f"{PREFIX}assets/img/{name}.webp"


def url(path):
    """Link to a page in the current language."""
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
]


def p_name(p):
    return p["name"][1 if LANG == "fr" else 0]


def p_place(p):
    return p["place"][1 if LANG == "fr" else 0] if p["place"] else ""


def p_kind(p):
    return p["kind"][1 if LANG == "fr" else 0]


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
    i = 1 if LANG == "fr" else 0
    label = t("Drag to change the time of day", "Faites glisser pour changer l'heure")
    return f'''<div class="compare {cls}"{' data-tease' if tease else ''}>
  <img src="{img(a)}" alt="{escape(la[i])}" loading="lazy">
  <div class="after"><img src="{img(b)}" alt="{escape(lb[i])}" loading="lazy"></div>
  <div class="compare-line"></div><div class="compare-handle" aria-hidden="true"></div>
  <span class="compare-tag l">{escape(la[i])}</span><span class="compare-tag r">{escape(lb[i])}</span>
  <input type="range" min="0" max="100" value="50" aria-label="{label}">
</div>'''


# ---------------------------------------------------------------- Layout
def nav_links():
    return [("projects.html", t("Projects", "Projets"), "projects"), ("plot-lab.html", t("Plot Lab", "Plot Lab"), "lab"),
            ("expertise.html", t("Expertise", "Expertise"), "expertise"), ("studio.html", t("Studio", "Studio"), "studio")]


def layout(path, title, desc, main, active="", extra_head="", extra_js="", i18n=None):
    global OTHER_PATH
    other = "en" if LANG == "fr" else "fr"
    links = "".join(f'<a href="{url(h)}"{" aria-current=page" if k == active else ""}>{escape(l)}</a>' for h, l, k in nav_links())
    mobile = "".join(f'<a class="display" href="{url(h)}">{escape(l)}</a>' for h, l, k in nav_links())
    i18n_tag = f"<script>window.MMA_I18N={json.dumps(i18n, ensure_ascii=False)}</script>" if i18n else ""
    wa = wa_link(t("Hello MMA, I would like to talk about a project.", "Bonjour MMA, je souhaite parler d'un projet."))
    return f'''<!doctype html>
<html lang="{LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="theme-color" content="#0B1A1F">
<link rel="alternate" hreflang="{other}" href="{PREFIX}{other}/{path}">
<link rel="icon" href="{PREFIX}assets/logo-mma-white.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geologica:SHRP,wght@0..100,200..600&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
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
    <span class="lang"><a href="{PREFIX}{other}/{path}" hreflang="{other}">{other.upper()}</a></span>
    <a class="btn" href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a>
    <button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
  </nav>
</header>
<div class="mobile-menu">
  {mobile}
  <a class="display" href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a>
  <div class="btn-row"><a class="link" href="{PREFIX}{other}/{path}" hreflang="{other}">{t("Français", "English")}</a></div>
</div>
<main id="main">
{main}
</main>
<footer class="foot">
  <div class="foot-grid">
    <div><img class="foot-logo" src="{PREFIX}assets/logo-full-white.png" alt="MMA, Mharrech Mribah Architects" loading="lazy"></div>
    <div><h4>{t("Explore", "Explorer")}</h4><ul>{"".join(f'<li><a href="{url(h)}">{escape(l)}</a></li>' for h, l, k in nav_links())}</ul></div>
    <div><h4>{t("Talk to us", "Nous parler")}</h4><ul>
      <li><a href="tel:+{PHONES[0][1]}">{PHONES[0][0]}</a></li>
      <li><a href="tel:+{PHONES[1][1]}">{PHONES[1][0]}</a></li>
      <li><a href="{wa}" target="_blank" rel="noopener">WhatsApp</a></li>
    </ul></div>
    <div><h4>{t("Studio", "Studio")}</h4><ul><li>{t("Tangier, Morocco", "Tanger, Maroc")}</li><li><a href="{url("contact.html")}">{t("Start a project", "Lancer un projet")}</a></li></ul></div>
  </div>
  <div class="foot-end"><span>© 2026 MMA, Mharrech Mribah Architects</span><span>{t("Images are design visualizations.", "Les images sont des visualisations du projet.")}</span></div>
</footer>
<div class="dock">
  <div class="dock-menu">
    <a href="{wa}" target="_blank" rel="noopener">WhatsApp</a>
    <a href="tel:+{PHONES[0][1]}">{PHONES[0][0]}</a>
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
    return f'''<section class="final">
  <img src="{img(image)}" alt="" loading="lazy" data-parallax="5">
  <div class="final-body">
    <h2 class="display d-l" data-lines>{t("Bring us the plot. We'll show you what it can become.", "Apportez le terrain. Nous vous montrons ce qu'il peut devenir.")}</h2>
    <div class="btn-row" data-reveal>{btn(t("Start your project", "Lancer votre projet"), url("contact.html"))}{btn(t("Test it in 3D first", "Le tester d'abord en 3D"), url("plot-lab.html"), "ghost")}</div>
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

    tower = by_slug("residential-tower-tangier")
    loc = "fr-FR" if LANG == "fr" else "en-GB"
    steps = [
        (t("The rules take most of it", "Les règles en prennent l'essentiel"),
         t("A 4,604 m² plot looked like an easy win. Once the planning rules were applied, only 1,353 m² remained buildable. This is where most projects lose money, before anyone notices.",
           "Un terrain de 4 604 m² semblait une évidence. Après application des règles d'urbanisme, il ne restait que 1 353 m² constructibles. C'est là que la plupart des projets perdent de l'argent, avant que personne ne s'en aperçoive.")),
        (t("We test the volume", "Nous testons le volume"),
         t("Base, main body and upper levels are tested against the limits until the building earns its height on that exact plot.",
           "Socle, corps principal et émergence sont testés face aux limites, jusqu'à ce que le bâtiment justifie sa hauteur sur ce terrain précis.")),
        (t("We draw every floor to work", "Chaque étage est dessiné pour servir"),
         t("Apartment by apartment, the floor plate is drawn so that the building you can sell or rent matches the building you can build.",
           "Appartement après appartement, l'étage est dessiné pour que ce que vous pouvez vendre ou louer corresponde à ce que vous pouvez construire.")),
        (t("A restricted plot becomes an address", "Un terrain contraint devient une adresse"),
         t("Two minutes on foot from Tanger Ville station, the constraint has turned into the building's identity.",
           "À deux minutes à pied de la gare Tanger Ville, la contrainte est devenue l'identité du bâtiment.")),
    ]
    frames = ["tower-d1", "tower-d3", "tower-plan", "tower-1"]
    frame_html = "".join(f'<img src="{img(f)}" alt="" loading="lazy"{" class=full" if f == "tower-1" else ""}>' for f in frames)
    step_html = "".join(f'<div class="story-step"><h3 class="display d-s">{escape(a)}</h3><p class="muted">{escape(b)}</p></div>' for a, b in steps)
    bars_story = "<i></i>" * len(steps)

    rail_order = ["hotel-chefchaouen", "180-apartments-tangier", "villa-guest-house-estate", "villa-maresvista", "beachfront-resort", "residence-alma", "suites-tower"]
    rail = "".join(pcard(by_slug(s)) for s in rail_order)

    marquee_items = [(f"{num(27024)} m²", t("largest scheme", "plus grand projet")), ("180", t("apartments in one building", "appartements dans un immeuble")),
                     (t("4 stars", "4 étoiles"), t("hotel in Chefchaouen", "hôtel à Chefchaouen")), (t("2 min", "2 min"), t("from the TGV station", "de la gare TGV")),
                     (t("8 projects", "8 projets"), t("in the selected works", "dans la sélection"))]
    marquee = "".join(f"<span>{escape(a)} <small>{escape(b)}</small></span>" for a, b in marquee_items)

    type_rows = ""
    float_imgs = ""
    for key, im, title, q, slug in TYPES:
        i = 1 if LANG == "fr" else 0
        type_rows += f'<a class="type" data-float="{key}" href="{url("expertise.html")}#{key}"><span class="display d-m">{escape(title[i])}</span><p class="muted">{escape(q[i])}</p></a>'
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

<section class="section wrap">
  <p class="display statement">{t("The decisions that make or lose the most money are taken before the first wall goes up. What the plot allows. What the building can hold. What it will feel like to live in, stay in or buy. We make those decisions visible, while they can still change.",
    "Les décisions qui font gagner ou perdre le plus d'argent se prennent avant le premier mur. Ce que le terrain permet. Ce que le bâtiment peut contenir. Ce qu'on y ressentira en y vivant, en y séjournant ou en l'achetant. Nous rendons ces décisions visibles, tant qu'elles peuvent encore changer.")}</p>
</section>

<section class="story">
  <div class="story-pin">
    <div>
      <span class="eyebrow">{t("Case study · Tangier", "Étude de cas · Tanger")}</span>
      <p class="display story-num"><b data-from="4604" data-to="1353" data-locale="{loc}" style="font-weight:300">{num(4604)}</b><small>m²</small></p>
      <div class="story-steps">{step_html}</div>
      <div class="story-progress" aria-hidden="true">{bars_story}</div>
      <p style="margin-top:18px"><a class="link" href="{url("projects/" + tower["slug"] + ".html")}">{t("See the full project", "Voir le projet complet")}</a></p>
    </div>
    <div class="story-frames">{frame_html}</div>
  </div>
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

<section class="section wrap">
  <div class="remote">
    <div>
      <span class="eyebrow">{t("Living abroad or in another city?", "Vous vivez à l'étranger ou dans une autre ville ?")}</span>
      <h2 class="display d-l" style="margin-top:10px" data-lines>{t("Your site, in your pocket.", "Votre chantier, dans votre poche.")}</h2>
      <ul>
        <li>{t("A dated photo report every week", "Un rapport photo daté chaque semaine")}</li>
        <li>{t("Video walkthroughs of the site on request", "Des visites vidéo du chantier sur demande")}</li>
        <li>{t("Every plan, permit and contract in one shared folder", "Plans, permis et contrats dans un seul dossier partagé")}</li>
        <li>{t("Your approval before each stage moves forward", "Votre validation avant chaque nouvelle étape")}</li>
      </ul>
    </div>
    <div class="phone" data-reveal aria-label="{t("Example of a site update", "Exemple de suivi de chantier")}">
      <span class="example-tag">{t("Example", "Exemple")}</span>
      <div class="phone-screen">
        <div class="phone-top"><b>MMA</b><span>{t("Your project", "Votre projet")}</span></div>
        <div class="bubble"><img src="{img("estate-2")}" alt="" loading="lazy">{t("Week 12: first-floor slab poured. Next, second-floor walls.", "Semaine 12 : dalle du premier étage coulée. Ensuite, les murs du deuxième étage.")}</div>
        <div class="bubble">{t("Your choice needed: window frame finish, by Friday.", "Votre choix : finition des menuiseries, d'ici vendredi.")}</div>
        <div class="bubble me">{t("Approved. Let's go with the bronze.", "Validé. Partons sur le bronze.")}</div>
      </div>
    </div>
  </div>
</section>
{final_cta()}
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
    i = 1 if LANG == "fr" else 0
    specs = ""
    for label, n, unit in p["specs"]:
        if n is None:
            value = unit[i]
        else:
            value = f"{num(n)} {unit}".strip()
        specs += f"<div><dt>{escape(label[i])}</dt><dd>{escape(value)}</dd></div>"
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
      <h2 class="display d-l" data-lines>{escape(p["pitch"][i])}</h2>
      <p class="lede" style="margin-top:clamp(18px,2vw,30px)" data-reveal>{escape(p["text"][i])}</p>
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
    return layout(f'projects/{p["slug"]}.html', f"{p_name(p)} · MMA Architects", p["text"][i], main, "projects")


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
        "noGl": t("3D isn't available in this browser. You can still use the controls to see the figures.", "La 3D n'est pas disponible dans ce navigateur. Les réglages restent utilisables pour voir les chiffres."),
    }}
    th = "".join(f"<th scope=col>{escape(x)}</th>" for x in [t("Option", "Option"), t("Type", "Type"), t("Plot", "Terrain"), t("Coverage", "Emprise"), t("Levels", "Niveaux"), t("Floor area", "Surface"), t("Capacity", "Capacité"), t("Finish", "Finition"), t("Budget (MAD)", "Budget (MAD)"), ""])
    main = f'''
<section class="lab" id="labRoot">
  <div class="lab-stage">
    <div class="lab-canvas" aria-label="{t("3D model of the building on the plot. Drag to turn it.", "Modèle 3D du bâtiment sur le terrain. Faites glisser pour le tourner.")}"></div>
    <div class="lab-title">
      <h1 class="display d-l" data-lines>{t("Plot Lab", "Plot Lab")}</h1>
      <p style="margin-top:6px;max-width:27em">{t("Shape a first idea of your project, then send it to the architects.", "Dessinez une première idée de votre projet, puis envoyez-la aux architectes.")}</p>
    </div>
    <p class="lab-hint">{t("Drag to turn · Scroll or pinch to zoom", "Glissez pour tourner · Molette ou pincement pour zoomer")}</p>
  </div>
  <aside class="lab-panel" aria-label="{t("Study controls", "Réglages de l'étude")}">
    <div class="seg" role="group" aria-label="{t("Type of project", "Type de projet")}">{prog}</div>
    <div class="ctl"><label for="labArea"><span>{t("Plot size", "Surface du terrain")}</span><output id="outArea"></output></label><input id="labArea" type="range" step="50"></div>
    <div class="ctl"><label for="labCover"><span>{t("Coverage of the plot", "Emprise au sol")}</span><output id="outCover"></output></label><input id="labCover" type="range" step="5"></div>
    <div class="ctl"><label for="labFloors"><span>{t("Levels", "Niveaux")}</span><output id="outFloors"></output></label><input id="labFloors" type="range" step="1"></div>
    <div class="ctl"><label for="labHour"><span>{t("Time of day", "Heure de la journée")}</span><output id="outHour"></output></label><input id="labHour" type="range" min="6" max="21" step="0.25"><button class="link" id="labPlay" type="button" style="font-size:13px;margin-top:3px">{t("Play the day", "Lancer la journée")}</button></div>
    <div class="seg" role="group" aria-label="{t("Level of finish", "Niveau de finition")}">{fin}</div>
    <div class="lab-res" aria-live="polite">
      <div><span>{t("Floor area", "Surface de plancher")}</span><strong id="resFloor"></strong></div>
      <div><span>{t("Rough capacity", "Capacité estimée")}</span><strong id="resCap"></strong></div>
      <div class="wide"><span>{t("First budget, excluding land", "Premier budget, hors terrain")}</span><strong id="resBudget"></strong></div>
    </div>
    <div class="lab-actions">
      <a class="btn" id="labSend" href="{url("contact.html")}">{t("Send this study to MMA", "Envoyer cette étude à MMA")} {ARROW}</a>
      <button class="mini" id="labSave" type="button">{t("Save option", "Garder l'option")}</button>
      <button class="mini" id="labShare" type="button">{t("Copy link", "Copier le lien")}</button>
    </div>
    <p class="note">{t("Illustrative only, using sample rates that MMA will confirm. Real limits come from your plot's planning rules. Capacity assumes 85 m² per apartment and 40 m² per room. Sun position is indicative.",
      "À titre indicatif, avec des tarifs d'exemple que MMA confirmera. Les limites réelles dépendent des règles d'urbanisme de votre terrain. Capacité sur la base de 85 m² par appartement et 40 m² par chambre. Position du soleil indicative.")}</p>
  </aside>
</section>
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
    stages = [
        (t("Feasibility", "Faisabilité"), t("We read the planning rules and test what the plot can really hold, before you commit further.", "Nous lisons les règles d'urbanisme et testons ce que le terrain peut réellement accueillir, avant d'aller plus loin.")),
        (t("Concept", "Esquisse"), t("Layouts, volumes and 3D views you can compare and react to.", "Plans, volumes et vues 3D à comparer et à commenter.")),
        (t("Developed design", "Avant-projet"), t("The chosen concept, measured and coordinated: plans, sections, façades, materials.", "L'esquisse retenue, mesurée et coordonnée : plans, coupes, façades, matériaux.")),
        (t("Building permit", "Permis de construire"), t("We prepare and file the application, then follow it with the authorities.", "Nous préparons et déposons le dossier, puis nous le suivons auprès des autorités.")),
        (t("Contractors", "Entreprises"), t("Construction documents and comparable quotes, with a clear recommendation.", "Dossier d'exécution et devis comparables, avec une recommandation claire.")),
        (t("Site supervision", "Suivi de chantier"), t("Regular visits and reports through to handover.", "Visites régulières et comptes rendus jusqu'à la réception.")),
    ]
    stage_html = "".join(f'<article class="stage"><b>{n + 1}</b><h3>{escape(a)}</h3><p>{escape(b)}</p></article>' for n, (a, b) in enumerate(stages))
    details = {
        "home": [t("Designs that fit the plot and how you live", "Un projet adapté au terrain et à votre façon de vivre"), t("Views, shade, privacy and orientation resolved early", "Vues, ombre, intimité et orientation réglées tôt"), t("Pools, gardens and terraces drawn as one composition", "Piscines, jardins et terrasses dessinés d'un seul geste")],
        "rental": [t("Unit mix tested against what the rules allow", "Typologies testées face à ce que les règles permettent"), t("Plans drawn for easy sale or rental", "Des plans pensés pour la vente ou la location"), t("Parking, circulation and shared spaces that hold up", "Parking, circulations et parties communes qui tiennent")],
        "hospitality": [t("Rooms, circulation and services balanced from the start", "Chambres, circulations et services équilibrés dès le départ"), t("Arrival, lobby and room design as one experience", "Arrivée, hall et chambres pensés comme une seule expérience"), t("Design that uses the site's view as its main asset", "Un projet qui fait de la vue son premier atout")],
        "estate": [t("Master plan across several buildings", "Plan d'ensemble sur plusieurs bâtiments"), t("Privacy between homes on a shared site", "Intimité entre les maisons sur un site partagé"), t("Shared gardens, event and guest spaces", "Jardins communs, espaces d'accueil et de réception")],
    }
    items = ""
    for key, im, title, q, slug in TYPES:
        i = 1 if LANG == "fr" else 0
        checks = "".join(f"<li>{escape(c)}</li>" for c in details[key])
        items += f'''<article class="invest-item" id="{key}">
  <div class="ii-img" data-reveal="img"><img src="{img(im)}" alt="" loading="lazy"></div>
  <div>
    <h3 class="display d-m">{escape(title[i])}</h3>
    <p class="muted" style="margin-top:10px">{escape(q[i])}</p>
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
    <div class="fact"><strong data-count="27024" data-locale="{"fr-FR" if LANG == "fr" else "en-GB"}" data-unit=" m²">{num(27024)} m²</strong><span>{t("floor area on the largest scheme", "de plancher sur le plus grand projet")}</span></div>
    <div class="fact"><strong data-count="180" data-locale="en-GB">180</strong><span>{t("apartments in one building", "appartements dans un immeuble")}</span></div>
    <div class="fact"><strong data-count="6250" data-locale="{"fr-FR" if LANG == "fr" else "en-GB"}" data-unit=" m²">{num(6250)} m²</strong><span>{t("4-star hotel in Chefchaouen", "hôtel 4 étoiles à Chefchaouen")}</span></div>
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
    <article class="partner" data-reveal="img"><img src="{img("maresvista-3")}" alt="" loading="lazy"><div class="partner-body"><span class="eyebrow" style="color:inherit">{t("Architect, partner", "Architecte, associé(e)")}</span><h2 class="display d-m" style="margin-top:6px">Mharrech</h2></div></article>
    <article class="partner" data-reveal="img"><img src="{img("suites-3")}" alt="" loading="lazy"><div class="partner-body"><span class="eyebrow" style="color:inherit">{t("Architect, partner", "Architecte, associé(e)")}</span><h2 class="display d-m" style="margin-top:6px">Mribah</h2></div></article>
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
        <a class="btn ghost" href="tel:+{PHONES[0][1]}">{t("Call", "Appeler")} {PHONES[0][0]}</a>
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


# ---------------------------------------------------------------- Build
def write(rel, html):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def build():
    global LANG, PREFIX
    count = 0
    for LANG in ("en", "fr"):
        PREFIX = "../"
        for name, fn in (("index", page_home), ("projects", page_projects), ("plot-lab", page_lab), ("expertise", page_expertise), ("studio", page_studio), ("contact", page_contact)):
            write(f"{LANG}/{name}.html", fn())
            count += 1
        PREFIX = "../../"
        for i, p in enumerate(PROJECTS):
            write(f'{LANG}/projects/{p["slug"]}.html', page_project(p, PROJECTS[(i + 1) % len(PROJECTS)]))
            count += 1
    write("index.html", '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>MMA Architects</title>
<meta http-equiv="refresh" content="0;url=fr/index.html">
<script>location.replace((navigator.language||'fr').toLowerCase().startsWith('fr')?'fr/index.html':'en/index.html')</script>
</head><body><a href="fr/index.html">Français</a> · <a href="en/index.html">English</a></body></html>
''')
    write("404.html", '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable · MMA Architects</title><meta name="robots" content="noindex">
<style>body{margin:0;min-height:100svh;display:grid;place-content:center;gap:14px;padding:24px;background:#0B1A1F;color:#EFEDE8;font:400 18px/1.5 system-ui,sans-serif}img{width:150px;height:auto}a{color:#F0A35E}</style>
</head><body><img src="/assets/logo-mma-white.png" alt="MMA, Mharrech Mribah Architects">
<p>Cette page n'existe pas. <a href="/fr/index.html">Retour à l'accueil</a></p>
<p>This page doesn't exist. <a href="/en/index.html">Back to home</a></p>
</body></html>
''')
    print(f"Built {count} pages")


if __name__ == "__main__":
    build()
