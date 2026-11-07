# MMA Architects website

Static site with full pages in French (`fr/`), English (`en/`), Spanish (`es/`), Arabic (`ar/`) and Chinese (`zh/`). Pages are generated from `build.py`.

- Edit English and French text and projects in `build.py`, then run `python3 build.py`.
- Spanish, Arabic and Chinese text is in `translations.py`, keyed by the English. If an English string changes, the build stops and lists what to update.
- The team doesn't read Chinese, so WhatsApp messages from the Chinese pages carry the English too. Anything the visitor types is sent as written.
- Styles are in `css/site.css`, shared motion in `js/site.js`, the 3D Plot Lab in `js/lab.js`, its sun and plot maths in `js/plot-geo.js`, and its map in `js/plot-map.js`.
- Preview through a local server (the 3D model needs one): `python3 -m http.server 8123`.
- After changing `build.py`, run it and commit the regenerated `en/`, `fr/`, `es/`, `ar/`, `zh/` and `404.html`. The container serves those files and does not run the build.
- Sample construction rates live in `build.py` (`page_lab`) and fee and contingency percentages in `js/lab.js` (`calc`).

## Deploying with Coolify

1. Push this folder to a private Git repository, with this folder as the repository root.
2. In Coolify, create a new resource from that repository.
3. Set **Build Pack** to `Dockerfile`, **Base Directory** to `/`, and **Ports Exposes** to `80`.
4. Add the domain, for example `https://preview.example.com`, and deploy.
5. Check `/healthz` returns `ok`, then open the site. The root URL sends visitors to `/fr/`, the main language; the other languages are reached from the switch in the header.

### Going public

The site is currently hidden from search engines. When the client approves it:

- remove every `X-Robots-Tag` line from `nginx.conf`
- change `robots.txt` to `Allow: /`
- replace the Plot Lab satellite imagery: set `IMAGERY_URL` and `IMAGERY_CREDIT` in `build.py` to a provider licensed for commercial use, using a key limited to the site's domain, then rebuild. The current keyless Esri service is for the preview only.
- review the OpenStreetMap tile and Nominatim search usage policies against the expected traffic, and move to a paid provider if needed
- add the Plot Lab's map services to the site's privacy information
