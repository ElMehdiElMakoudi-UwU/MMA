# MMA Architects website

Static site with full pages in French (`fr/`), English (`en/`), Spanish (`es/`) and Arabic (`ar/`), plus one Chinese landing page (`zh/`). Pages are generated from `build.py`.

- Edit English and French text and projects in `build.py`, then run `python3 build.py`.
- Spanish, Arabic and Chinese layout text is in `translations.py`, keyed by the English. If an English string changes, the build stops and lists what to update. The Chinese page's own content is in `page_zh()` in `build.py`.
- Styles are in `css/site.css`, shared motion in `js/site.js`, the 3D Plot Lab in `js/lab.js`.
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
