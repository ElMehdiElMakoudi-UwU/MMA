/* Plot Lab map: find a place, click the corners of the plot. Leaflet only loads when this opens. */
import { toLocal, polygonArea, selfIntersects, PLOT_MIN, PLOT_MAX } from './plot-geo.js';

const LEAFLET = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/';
const SEARCH = 'https://nominatim.openstreetmap.org/search';
/* Corners placed further out than this would not be accurate enough to measure a plot */
const MIN_DRAW_ZOOM = 16;

let leaflet = null;
function loadLeaflet() {
  if (!leaflet) {
    leaflet = new Promise((resolve, reject) => {
      const css = document.createElement('link');
      css.rel = 'stylesheet'; css.href = `${LEAFLET}leaflet.min.css`;
      document.head.append(css);
      const js = document.createElement('script');
      js.src = `${LEAFLET}leaflet.min.js`;
      js.onload = () => resolve(window.L);
      js.onerror = () => { leaflet = null; reject(new Error('Leaflet failed to load')); };
      document.head.append(js);
    });
  }
  return leaflet;
}

let picker = null;

function setUp(L, I, locale) {
  const dlg = document.getElementById('plotDialog');
  const $ = s => dlg.querySelector(s);
  const status = $('#plotStatus'), results = $('#plotResults'), useBtn = $('#plotUse');

  const map = L.map($('#plotMap'), { zoomControl: true, attributionControl: true, maxZoom: 21 });
  map.attributionControl.setPrefix(false);
  const satellite = L.tileLayer(I.imagery, { maxNativeZoom: 19, maxZoom: 21, attribution: I.imageryCredit });
  const street = L.tileLayer(I.street, { maxNativeZoom: 19, maxZoom: 21, attribution: I.streetCredit });
  satellite.addTo(map);

  const shape = L.polygon([], { color: '#F0A35E', weight: 2, fillOpacity: .22 }).addTo(map);
  let corners = [], done = null;

  const latLngs = () => corners.map(m => { const p = m.getLatLng(); return [p.lat, L.Util.wrapNum(p.lng, [-180, 180], true)]; });

  function say(text, isError) {
    status.textContent = text;
    status.classList.toggle('err', !!isError);
  }
  function refresh() {
    shape.setLatLngs(corners.map(m => m.getLatLng()));
    $('#plotUndo').disabled = !corners.length;
    $('#plotClear').disabled = !corners.length;
    useBtn.disabled = true;
    if (corners.length < 3) { say(corners.length ? I.moreCorners : I.drawHint); return; }
    const { points } = toLocal(latLngs());
    const area = polygonArea(points);
    if (selfIntersects(points)) say(I.crossing, true);
    else if (area < PLOT_MIN) say(I.tooSmall.replace('{n}', PLOT_MIN.toLocaleString(locale)), true);
    else if (area > PLOT_MAX) say(I.tooLarge.replace('{n}', PLOT_MAX.toLocaleString(locale)), true);
    else { useBtn.disabled = false; say(I.measured.replace('{area}', Math.round(area).toLocaleString(locale))); }
  }
  function addCorner(latlng) {
    if (map.getZoom() < MIN_DRAW_ZOOM) {
      map.flyTo(latlng, MIN_DRAW_ZOOM + 1, { duration: .7 });
      say(I.zoomIn);
      return;
    }
    const m = L.marker(latlng, { draggable: true, keyboard: false, icon: L.divIcon({ className: 'plot-corner', iconSize: [18, 18] }) });
    m.on('drag dragend', refresh);
    m.addTo(map);
    corners.push(m);
    refresh();
  }
  function clearCorners() {
    corners.forEach(m => m.remove());
    corners = [];
  }
  map.on('click', e => addCorner(e.latlng));

  $('#plotUndo').addEventListener('click', () => { const m = corners.pop(); if (m) m.remove(); refresh(); });
  $('#plotClear').addEventListener('click', () => { clearCorners(); refresh(); });
  /* For keyboards, and for precise placement on small touch screens */
  $('#plotAddCentre').addEventListener('click', () => addCorner(map.getCenter()));

  dlg.querySelectorAll('[data-layer]').forEach(b => b.addEventListener('click', () => {
    const toStreet = b.dataset.layer === 'street';
    map.removeLayer(toStreet ? satellite : street);
    (toStreet ? street : satellite).addTo(map);
    dlg.querySelectorAll('[data-layer]').forEach(x => x.setAttribute('aria-pressed', x === b));
  }));

  /* Search, or go straight to typed coordinates */
  let lastSearch = 0;
  $('#plotSearch').addEventListener('submit', async e => {
    e.preventDefault();
    const text = $('#plotQuery').value.trim();
    results.textContent = '';
    if (!text) return;
    const coords = text.match(/^(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)$/);
    if (coords && Math.abs(+coords[1]) <= 85 && Math.abs(+coords[2]) <= 180) {
      map.flyTo([+coords[1], +coords[2]], 18, { duration: .9 });
      return;
    }
    /* The public search service allows one request a second */
    if (Date.now() - lastSearch < 1100) return;
    lastSearch = Date.now();
    const btn = $('#plotSearch button');
    btn.disabled = true;
    try {
      const params = new URLSearchParams({ q: text, format: 'jsonv2', limit: 5, 'accept-language': document.documentElement.lang, viewbox: '-17.1,35.95,-1,21', bounded: 0 });
      const res = await fetch(`${SEARCH}?${params}`);
      if (!res.ok) throw new Error(res.status);
      const found = await res.json();
      if (!found.length) say(I.searchNone, true);
      else if (found.length === 1) goTo(found[0]);
      else found.forEach(f => {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = f.display_name;
        b.addEventListener('click', () => { results.textContent = ''; goTo(f); });
        results.append(b);
      });
    } catch (err) {
      say(I.searchFail, true);
    }
    btn.disabled = false;
  });
  function goTo(f) {
    if (f.boundingbox) {
      const [s, n, w, e] = f.boundingbox.map(Number);
      map.flyToBounds([[s, w], [n, e]], { maxZoom: 18, duration: .9 });
    } else map.flyTo([+f.lat, +f.lon], 17, { duration: .9 });
  }

  const gps = $('#plotGps');
  if (!navigator.geolocation) gps.classList.add('hide');
  gps.addEventListener('click', () => {
    gps.disabled = true;
    navigator.geolocation.getCurrentPosition(
      p => { gps.disabled = false; map.flyTo([p.coords.latitude, p.coords.longitude], 18, { duration: .9 }); },
      () => { gps.disabled = false; say(I.gpsFail, true); },
      { enableHighAccuracy: true, timeout: 12000 }
    );
  });

  const finish = value => {
    const cb = done;
    done = null;
    if (dlg.open) dlg.close();
    if (window.MMA_LENIS) window.MMA_LENIS.start();
    if (cb) cb(value);
  };
  useBtn.addEventListener('click', () => finish(latLngs()));
  $('#plotCancel').addEventListener('click', () => finish(null));
  dlg.addEventListener('close', () => finish(null));

  return {
    open({ initial, centre }) {
      return new Promise(resolve => {
        done = resolve;
        clearCorners();
        results.textContent = '';
        if (window.MMA_LENIS) window.MMA_LENIS.stop();
        dlg.showModal();
        map.invalidateSize();
        if (initial) {
          map.fitBounds(initial, { padding: [40, 40], maxZoom: 19, animate: false });
          initial.forEach(p => {
            const m = L.marker(p, { draggable: true, keyboard: false, icon: L.divIcon({ className: 'plot-corner', iconSize: [18, 18] }) });
            m.on('drag dragend', refresh);
            m.addTo(map);
            corners.push(m);
          });
        } else map.setView(centre, 14, { animate: false });
        refresh();
      });
    }
  };
}

export async function openPlotPicker({ I, locale, initial, centre }) {
  const L = await loadLeaflet();
  picker = picker || setUp(L, I, locale);
  return picker.open({ initial, centre });
}
