/* Plot Lab maths with no browser or 3D dependencies: the sun's real position,
   local clock time, and fitting a building footprint inside a drawn plot.
   Scene axes: +x is east, +z is south, so north is -z. */

const RAD = Math.PI / 180;
const M_PER_DEG = 111320;

/* ------------------------------------------------------------------ Sun
   NOAA solar position equations. Returns degrees: altitude above the horizon
   (with atmospheric refraction) and azimuth clockwise from north. */
export function sunPosition(date, lat, lng) {
  const jc = (date.getTime() / 86400000 + 2440587.5 - 2451545) / 36525;
  const meanLong = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360;
  const meanAnom = 357.52911 + jc * (35999.05029 - 0.0001537 * jc);
  const ecc = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc);
  const m = meanAnom * RAD;
  const centre = Math.sin(m) * (1.914602 - jc * (0.004817 + 0.000014 * jc))
    + Math.sin(2 * m) * (0.019993 - 0.000101 * jc) + Math.sin(3 * m) * 0.000289;
  const appLong = meanLong + centre - 0.00569 - 0.00478 * Math.sin((125.04 - 1934.136 * jc) * RAD);
  const obliqMean = 23 + (26 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60) / 60;
  const obliq = (obliqMean + 0.00256 * Math.cos((125.04 - 1934.136 * jc) * RAD)) * RAD;
  const decl = Math.asin(Math.sin(obliq) * Math.sin(appLong * RAD));
  const y = Math.tan(obliq / 2) ** 2;
  const l0 = meanLong * RAD;
  const eqTime = 4 / RAD * (y * Math.sin(2 * l0) - 2 * ecc * Math.sin(m)
    + 4 * ecc * y * Math.sin(m) * Math.cos(2 * l0) - 0.5 * y * y * Math.sin(4 * l0) - 1.25 * ecc * ecc * Math.sin(2 * m));
  const utcMin = ((date.getTime() % 86400000) + 86400000) % 86400000 / 60000;
  const solarMin = (((utcMin + eqTime + 4 * lng) % 1440) + 1440) % 1440;
  const hourAngle = (solarMin / 4 - 180) * RAD;
  const phi = lat * RAD;
  const cosZen = Math.max(-1, Math.min(1, Math.sin(phi) * Math.sin(decl) + Math.cos(phi) * Math.cos(decl) * Math.cos(hourAngle)));
  const zen = Math.acos(cosZen);
  const geom = 90 - zen / RAD;
  const azimuth = (Math.atan2(Math.sin(hourAngle), Math.cos(hourAngle) * Math.sin(phi) - Math.tan(decl) * Math.cos(phi)) / RAD + 180 + 360) % 360;
  return { altitude: geom + refraction(geom), geometric: geom, azimuth };
}

function refraction(alt) {
  if (alt > 85) return 0;
  const te = Math.tan(alt * RAD);
  let arcsec;
  if (alt > 5) arcsec = 58.1 / te - 0.07 / te ** 3 + 0.000086 / te ** 5;
  else if (alt > -0.575) arcsec = 1735 + alt * (-518.2 + alt * (103.4 + alt * (-12.79 + alt * 0.711)));
  else arcsec = -20.772 / te;
  return arcsec / 3600;
}

/* ---------------------------------------------------------------- Clock */
const zoneFormats = new Map();
/* Morocco moved to permanent UTC+0 on 20 September 2026. Devices with older time zone data still say UTC+1. */
const MOROCCO_UTC = Date.UTC(2026, 8, 20, 2);
export function zoneOffsetMin(ms, tz) {
  if ((tz === 'Africa/Casablanca' || tz === 'Africa/El_Aaiun') && ms >= MOROCCO_UTC) return 0;
  let f = zoneFormats.get(tz);
  if (!f) {
    f = new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' });
    zoneFormats.set(tz, f);
  }
  const p = {};
  f.formatToParts(new Date(ms)).forEach(x => { p[x.type] = +x.value; });
  return Math.round((Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second) - Math.floor(ms / 1000) * 1000) / 60000);
}

/* A clock reading at the plot: uses its time zone, or a longitude estimate when none is known */
export function clockToDate(year, dayOfYear, hour, where) {
  const guess = Date.UTC(year, 0, dayOfYear) + hour * 3600000;
  if (!where.tz) return new Date(guess - Math.round(where.lng / 15) * 3600000);
  const first = guess - zoneOffsetMin(guess, where.tz) * 60000;
  return new Date(guess - zoneOffsetMin(first, where.tz) * 60000);
}

export function offsetLabel(year, dayOfYear, where) {
  const min = where.tz ? zoneOffsetMin(clockToDate(year, dayOfYear, 12, where).getTime(), where.tz) : Math.round(where.lng / 15) * 60;
  const a = Math.abs(min), m = a % 60;
  return `UTC${min < 0 ? '−' : '+'}${Math.floor(a / 60)}${m ? `:${String(m).padStart(2, '0')}` : ''}`;
}

/* Sunrise and sunset as clock hours on that day, found from the sun's altitude.
   Either is null when the sun does not cross the horizon that day. */
export function sunTimes(year, dayOfYear, where) {
  /* The standard definition: the sun's upper edge on the horizon, at a geometric altitude of -0.833 degrees */
  const alt = h => sunPosition(clockToDate(year, dayOfYear, h, where), where.lat, where.lng).geometric + 0.833;
  const crossing = (a, b) => {
    let fa = alt(a);
    for (let i = 0; i < 24; i++) {
      const mid = (a + b) / 2, fm = alt(mid);
      if ((fa < 0) === (fm < 0)) { a = mid; fa = fm; } else b = mid;
    }
    return (a + b) / 2;
  };
  let rise = null, set = null;
  for (let h = 0; h < 24; h += .25) {
    const a = alt(h), b = alt(h + .25);
    if (a < 0 && b >= 0 && rise === null) rise = crossing(h, h + .25);
    if (a >= 0 && b < 0) set = crossing(h, h + .25);
  }
  return { rise, set };
}

export function dayOfYear(d = new Date()) {
  return Math.round((Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) - Date.UTC(d.getFullYear(), 0, 0)) / 86400000);
}

/* ---------------------------------------------------------------- Plot polygons
   latLngs are [lat, lng]; local points are [x, z] in metres around the plot centre. */
export function toLocal(latLngs) {
  const lat0 = latLngs.reduce((a, p) => a + p[0], 0) / latLngs.length;
  const lng0 = latLngs.reduce((a, p) => a + p[1], 0) / latLngs.length;
  const k = Math.cos(lat0 * RAD);
  return {
    lat0, lng0,
    points: latLngs.map(([lat, lng]) => [(lng - lng0) * M_PER_DEG * k, -(lat - lat0) * M_PER_DEG])
  };
}

export function polygonArea(pts) {
  let s = 0;
  pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; s += p[0] * q[1] - q[0] * p[1]; });
  return Math.abs(s) / 2;
}

const cross = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
function segmentsCross(a, b, c, d) {
  const d1 = cross(c, d, a), d2 = cross(c, d, b), d3 = cross(a, b, c), d4 = cross(a, b, d);
  return ((d1 > 0) !== (d2 > 0)) && ((d3 > 0) !== (d4 > 0)) && d1 && d2 && d3 && d4;
}

export function selfIntersects(pts) {
  const n = pts.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 2; j < n; j++) {
      if (i === 0 && j === n - 1) continue;
      if (segmentsCross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n])) return true;
    }
  }
  return false;
}

export function pointInPolygon(p, pts) {
  let inside = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const a = pts[i], b = pts[j];
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside;
}

function centroid(pts) {
  let a = 0, x = 0, z = 0;
  pts.forEach((p, i) => {
    const q = pts[(i + 1) % pts.length], c = p[0] * q[1] - q[0] * p[1];
    a += c; x += (p[0] + q[0]) * c; z += (p[1] + q[1]) * c;
  });
  return Math.abs(a) < 1e-9 ? pts[0] : [x / (3 * a), z / (3 * a)];
}

/* The building's direction: along the longest side, with its front (local +z) facing as far south as it can.
   Local (x, z) to plot: X = x cos r + z sin r, Z = z cos r - x sin r, the same as a three.js rotation.y of r. */
function plotRotation(pts) {
  let best = 0, r = 0;
  pts.forEach((p, i) => {
    const q = pts[(i + 1) % pts.length], dx = q[0] - p[0], dz = q[1] - p[1], len = Math.hypot(dx, dz);
    if (len > best) { best = len; r = -Math.atan2(dz, dx); }
  });
  /* Front direction in plot axes is (sin r, cos r); +z is south */
  if (Math.cos(r) < 0) r += Math.PI;
  return r;
}

const toFrame = (p, r) => [p[0] * Math.cos(r) - p[1] * Math.sin(r), p[0] * Math.sin(r) + p[1] * Math.cos(r)];
const fromFrame = (p, r) => [p[0] * Math.cos(r) + p[1] * Math.sin(r), p[1] * Math.cos(r) - p[0] * Math.sin(r)];

function rectFits(poly, cx, cz, w, d) {
  const c = [[cx - w / 2, cz - d / 2], [cx + w / 2, cz - d / 2], [cx + w / 2, cz + d / 2], [cx - w / 2, cz + d / 2]];
  for (const p of c) if (!pointInPolygon(p, poly)) return false;
  for (const p of poly) if (p[0] > c[0][0] && p[0] < c[1][0] && p[1] > c[0][1] && p[1] < c[2][1]) return false;
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    for (let k = 0; k < 4; k++) if (segmentsCross(a, b, c[k], c[(k + 1) % 4])) return false;
  }
  return true;
}

/* The largest rectangle of a set shape, up to the wanted area, that fits inside the plot.
   Ratios are tried from the preferred one outwards, so the building keeps its proportions
   whenever it can. `back` slides the building towards the rear of the plot (0 to 1). */
const fitCache = new Map();
export function fitFootprint(points, targetArea, ratio, back = 0) {
  const key = `${points.map(p => p.map(v => v.toFixed(2))).join(';')}|${targetArea.toFixed(1)}|${ratio}|${back}`;
  if (fitCache.has(key)) return fitCache.get(key);

  const rotation = plotRotation(points);
  const poly = points.map(p => toFrame(p, rotation));
  const xs = poly.map(p => p[0]), zs = poly.map(p => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minZ = Math.min(...zs), maxZ = Math.max(...zs);
  const mid = toFrame(centroid(points), rotation);
  const prefer = [mid[0], mid[1] - back * (mid[1] - minZ)];

  const N = 26, candidates = [];
  for (let i = 0; i <= N; i++) {
    for (let j = 0; j <= N; j++) {
      const c = [minX + (maxX - minX) * i / N, minZ + (maxZ - minZ) * j / N];
      if (pointInPolygon(c, poly)) candidates.push({ c, dist: Math.hypot(c[0] - prefer[0], c[1] - prefer[1]) });
    }
  }
  candidates.push({ c: mid, dist: Math.hypot(mid[0] - prefer[0], mid[1] - prefer[1]) });
  candidates.sort((a, b) => a.dist - b.dist);

  const ratios = [ratio, ratio * .9, ratio * 1.15, ratio * .8, ratio * 1.35, ratio * .7, ratio * 1.6, 1, ratio * 2, ratio * 2.5, 1 / ratio, 3.5, 5];
  let best = null;
  for (const rr of ratios) {
    const shape = a => [Math.sqrt(a * rr), a / Math.sqrt(a * rr)];
    for (const { c } of candidates) {
      if (best && best.area >= targetArea - .01) break;
      const floor = best ? best.area : 0;
      /* Skip this spot unless it beats the best area so far */
      const test = Math.min(targetArea, floor * 1.001 + .001);
      const [tw, td] = shape(test);
      if (!rectFits(poly, c[0], c[1], tw, td)) continue;
      let lo = test, hi = targetArea;
      const [hw, hd] = shape(hi);
      if (rectFits(poly, c[0], c[1], hw, hd)) lo = hi;
      else for (let i = 0; i < 12; i++) {
        const a = (lo + hi) / 2, [w, d] = shape(a);
        if (rectFits(poly, c[0], c[1], w, d)) lo = a; else hi = a;
      }
      const [w, d] = shape(lo);
      best = { area: lo, w, d, c };
    }
    if (best && best.area >= targetArea - .01) break;
  }
  const result = best
    ? { w: best.w, d: best.d, area: best.w * best.d, center: fromFrame(best.c, rotation), rotation }
    : { w: 0, d: 0, area: 0, center: [0, 0], rotation };
  if (fitCache.size > 400) fitCache.clear();
  fitCache.set(key, result);
  return result;
}

/* Whether a rectangle in the building's own axes, relative to its centre, sits inside the plot */
export function localRectInPlot(points, fit, x, z, w, d) {
  const poly = points.map(p => toFrame(p, fit.rotation));
  const c = toFrame(fit.center, fit.rotation);
  return rectFits(poly, c[0] + x, c[1] + z, w, d);
}

/* The square used before a real plot is drawn */
export const squarePlot = area => {
  const h = Math.sqrt(area) / 2;
  return [[-h, -h], [h, -h], [h, h], [-h, h]];
};

const footprintRatio = program => (program === 'apartments' ? 1.4 : program === 'hotel' ? 1.6 : 1.3);

/* The building footprint for a study. The 3D model and the figures both use this, so they always agree. */
export function footprintFor(s) {
  const points = s.plot ? s.plot.points : squarePlot(s.area);
  return { points, ...fitFootprint(points, s.area * s.cover / 100, footprintRatio(s.program), s.program === 'villa' ? .55 : 0) };
}

/* ---------------------------------------------------------------- Share links */
export function encodePlot(latLngs) {
  return latLngs.map(p => `${p[0].toFixed(6)},${p[1].toFixed(6)}`).join(';');
}

export function decodePlot(text) {
  if (!text) return null;
  const pts = text.split(';').map(s => s.split(',').map(Number));
  if (pts.length < 3 || pts.length > 60) return null;
  if (pts.some(p => p.length !== 2 || !Number.isFinite(p[0]) || !Number.isFinite(p[1]) || Math.abs(p[0]) > 85 || Math.abs(p[1]) > 180)) return null;
  const { points } = toLocal(pts);
  const area = polygonArea(points);
  if (area < PLOT_MIN || area > PLOT_MAX || selfIntersects(points)) return null;
  return pts;
}

export const PLOT_MIN = 50, PLOT_MAX = 100000;
