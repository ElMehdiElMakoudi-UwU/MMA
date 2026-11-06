# MMA Architects website

Static site in French (`fr/`) and English (`en/`). Pages are generated from `build.py`.

- Edit text and projects in `build.py`, then run `python3 build.py`.
- Styles are in `css/site.css`, shared motion in `js/site.js`, the 3D Plot Lab in `js/lab.js`.
- Preview through a local server (the 3D model needs one): `python3 -m http.server 8123`.
- After changing `build.py`, run it and commit the regenerated `en/`, `fr/` and `404.html`. The container serves those files and does not run the build.
- Sample construction rates live in `build.py` (`page_lab`) and fee and contingency percentages in `js/lab.js` (`calc`).

## Deploying with Coolify

1. Push this folder to a private Git repository, with this folder as the repository root.
2. In Coolify, create a new resource from that repository.
3. Set **Build Pack** to `Dockerfile`, **Base Directory** to `/`, and **Ports Exposes** to `80`.
4. Add the domain, for example `https://preview.example.com`, and deploy.
5. Check `/healthz` returns `ok`, then open the site. The root URL sends visitors to `/fr/` or `/en/`.

### Going public

The site is currently hidden from search engines. When the client approves it:

- remove every `X-Robots-Tag` line from `nginx.conf`
- change `robots.txt` to `Allow: /`
