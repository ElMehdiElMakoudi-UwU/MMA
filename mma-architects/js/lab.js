/* Plot Lab: a live 3D massing model on a real or sample plot, lit by the real sun. */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import {
  sunPosition, sunTimes, clockToDate, offsetLabel, dayOfYear, toLocal, polygonArea,
  footprintFor, localRectInPlot, encodePlot, decodePlot
} from './plot-geo.js';

const STOPS = [
  { h: 6, top: '#2b3a55', low: '#f0a77e', sun: '#ffb27a', power: 1.0, hemi: .55, glow: .5 },
  { h: 9, top: '#5e9fd6', low: '#d4e6ef', sun: '#fff1d9', power: 2.1, hemi: .72, glow: 0 },
  { h: 13, top: '#4a90d1', low: '#e0eef6', sun: '#ffffff', power: 2.2, hemi: .72, glow: 0 },
  { h: 17, top: '#557fb0', low: '#f5c89a', sun: '#ffd0a0', power: 2.1, hemi: .75, glow: 0 },
  { h: 19, top: '#2a3b63', low: '#f0915a', sun: '#ffb88a', power: .95, hemi: .78, glow: .9 },
  { h: 21, top: '#0b1428', low: '#1f2f4a', sun: '#8aa6d0', power: .16, hemi: .28, glow: 1.5 }
];
const colorA = new THREE.Color(), colorB = new THREE.Color();
const mix = (a, b, t, out) => out.copy(colorA.set(a)).lerp(colorB.set(b), t);

function hourStops(h) {
  const hour = Math.max(6, Math.min(21, h));
  for (let i = 0; i < STOPS.length - 1; i++) {
    if (hour <= STOPS[i + 1].h) return [STOPS[i], STOPS[i + 1], (hour - STOPS[i].h) / (STOPS[i + 1].h - STOPS[i].h)];
  }
  return [STOPS[4], STOPS[5], 1];
}

/* Sky and light follow the sun's real height. Mornings and evenings have their own colours. */
const RISING = [[-8, STOPS[5]], [-.5, STOPS[0]], [9, STOPS[1]], [28, STOPS[2]]];
const SETTING = [[-8, STOPS[5]], [-.5, STOPS[4]], [9, STOPS[3]], [28, STOPS[2]]];
function altitudeStops(alt, list) {
  if (alt <= list[0][0]) return [list[0][1], list[0][1], 0];
  for (let i = 0; i < list.length - 1; i++) {
    if (alt <= list[i + 1][0]) return [list[i][1], list[i + 1][1], (alt - list[i][0]) / (list[i + 1][0] - list[i][0])];
  }
  return [list[3][1], list[3][1], 0];
}

const M_PER_DEG = 111320;
const tileX = (lng, n) => (lng + 180) / 360 * n;
const tileY = (lat, n) => (1 - Math.asinh(Math.tan(lat * Math.PI / 180)) / Math.PI) / 2 * n;
const tileLng = (x, n) => x / n * 360 - 180;
const tileLat = (y, n) => Math.atan(Math.sinh(Math.PI * (1 - 2 * y / n))) * 180 / Math.PI;

function seeded(n) { const x = Math.sin(n * 91.17) * 43758.5453; return x - Math.floor(x); }

export function createScene(host, opts = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, canvas: opts.canvas, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  if (!opts.canvas) host.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 1, 2000);
  camera.position.set(120, 80, 140);

  const skyUniforms = { top: { value: new THREE.Color() }, low: { value: new THREE.Color() } };
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 24, 12), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, uniforms: skyUniforms,
    vertexShader: 'varying float v;void main(){v=normalize(position).y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: 'uniform vec3 top;uniform vec3 low;varying float v;void main(){gl_FragColor=vec4(mix(low,top,smoothstep(-.02,.42,v)),1.);}'
  }));
  scene.add(sky);
  scene.fog = new THREE.Fog(0xffffff, 300, 860);

  const hemi = new THREE.HemisphereLight(0xffffff, 0x4a4f4a, 1);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -.0004;
  sun.shadow.normalBias = .4;
  scene.add(sun, sun.target);

  /* Materials */
  const M = {
    ground: new THREE.MeshStandardMaterial({ color: '#bfbcb2', roughness: 1 }),
    road: new THREE.MeshStandardMaterial({ color: '#a4a6a3', roughness: .95 }),
    plot: new THREE.MeshStandardMaterial({ color: '#efe6d6', roughness: 1 }),
    plotReal: new THREE.MeshStandardMaterial({ color: '#f0a35e', roughness: 1, transparent: true, opacity: .14, depthWrite: false }),
    garden: new THREE.MeshStandardMaterial({ color: '#7f9568', roughness: 1 }),
    plaster: new THREE.MeshStandardMaterial({ color: '#f4f0e8', roughness: .82 }),
    wood: new THREE.MeshStandardMaterial({ color: '#8a5d3b', roughness: .7 }),
    glass: new THREE.MeshStandardMaterial({ color: '#4d7c8e', roughness: .28, metalness: .12, emissive: '#ffb56b', emissiveIntensity: 0 }),
    neighbor: new THREE.MeshStandardMaterial({ color: '#ebe8e0', roughness: 1 }),
    water: new THREE.MeshStandardMaterial({ color: '#3fb6c6', roughness: .12, metalness: .25, emissive: '#27c3d8', emissiveIntensity: 0 }),
    leaf: new THREE.MeshStandardMaterial({ color: '#58734c', roughness: 1, flatShading: true }),
    bark: new THREE.MeshStandardMaterial({ color: '#5d4a3a', roughness: 1 })
  };

  const ground = new THREE.Mesh(new THREE.CircleGeometry(900, 48), M.ground);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -.6;
  ground.receiveShadow = true;
  scene.add(ground);

  const site = new THREE.Group(), building = new THREE.Group(), extras = new THREE.Group(), imagery = new THREE.Group();
  scene.add(site, building, extras, imagery);

  const box = (w, h, d, mat, x = 0, y = 0, z = 0, parent = building) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x, y + h / 2, z);
    m.castShadow = true; m.receiveShadow = true;
    parent.add(m);
    return m;
  };
  const clear = g => {
    while (g.children.length) {
      const c = g.children.pop();
      c.traverse(o => { if (o.geometry) o.geometry.dispose(); });
    }
  };
  const tree = (x, z, s, parent) => {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(.16 * s, .24 * s, 2.4 * s, 6), M.bark);
    t.position.set(x, 1.2 * s, z); t.castShadow = true; parent.add(t);
    const c = new THREE.Mesh(new THREE.IcosahedronGeometry(1.7 * s, 0), M.leaf);
    c.position.set(x, 3.3 * s, z); c.castShadow = true; c.scale.y = 1.15; parent.add(c);
  };

  const flatShape = points => {
    const shape = new THREE.Shape(points.map(p => new THREE.Vector2(p[0], -p[1])));
    const m = new THREE.Mesh(new THREE.ShapeGeometry(shape));
    m.rotation.x = -Math.PI / 2;
    m.receiveShadow = true;
    return m;
  };

  /* Satellite photo of the real surroundings, laid on the ground around the plot */
  let imageryRun = 0;
  function clearImagery() {
    imageryRun++;
    while (imagery.children.length) {
      const m = imagery.children.pop();
      m.geometry.dispose();
      if (m.material.map) m.material.map.dispose();
      m.material.dispose();
    }
  }
  /* A sharp layer around the plot, and a wider, coarser one out to the horizon */
  const plotSpan = points => Math.max(Math.max(...points.map(p => p[0])) - Math.min(...points.map(p => p[0])), Math.max(...points.map(p => p[1])) - Math.min(...points.map(p => p[1])));
  const imageryZoom = span => (span > 500 ? 16 : span > 250 ? 17 : 18);
  const REACH = 3;
  const tileMetres = (zoom, lat) => 40075016 / 2 ** zoom * Math.cos(lat * Math.PI / 180);
  const imageryRadius = (span, lat) => tileMetres(imageryZoom(span) - 2, lat) * (REACH + .5);
  function loadImagery(plot) {
    clearImagery();
    if (!opts.imageryUrl) return;
    const run = imageryRun, span = plotSpan(plot.points), inner = imageryZoom(span);
    const k = Math.cos(plot.lat0 * Math.PI / 180), loader = new THREE.TextureLoader();
    [[inner, -.2], [inner - 2, -.4]].forEach(([zoom, y]) => {
      const n = 2 ** zoom, cx = Math.floor(tileX(plot.lng0, n)), cy = Math.floor(tileY(plot.lat0, n));
      for (let ty = cy - REACH; ty <= cy + REACH; ty++) {
        for (let tx = cx - REACH; tx <= cx + REACH; tx++) {
          const west = (tileLng(tx, n) - plot.lng0) * M_PER_DEG * k, east = (tileLng(tx + 1, n) - plot.lng0) * M_PER_DEG * k;
          const north = -(tileLat(ty, n) - plot.lat0) * M_PER_DEG, south = -(tileLat(ty + 1, n) - plot.lat0) * M_PER_DEG;
          const url = opts.imageryUrl.replace('{z}', zoom).replace('{x}', tx).replace('{y}', ty);
          loader.load(url, tex => {
            if (run !== imageryRun) { tex.dispose(); return; }
            tex.colorSpace = THREE.SRGBColorSpace;
            tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
            const m = new THREE.Mesh(new THREE.PlaneGeometry(east - west, south - north), new THREE.MeshStandardMaterial({ map: tex, roughness: 1, color: '#c9c9c9' }));
            m.rotation.x = -Math.PI / 2;
            m.position.set((west + east) / 2, y, (north + south) / 2);
            m.receiveShadow = true;
            imagery.add(m);
            kick();
          }, undefined, () => {});
        }
      }
    });
  }

  /* A real plot sits on its own surroundings. The sample keeps its illustrative road, neighbours and planting. */
  let siteKey = '';
  function buildSite(s, points) {
    const key = s.plot ? s.plot.key : `sample ${s.area}`;
    if (key === siteKey) return;
    const wasReal = siteKey && !siteKey.startsWith('sample');
    siteKey = key;
    clear(site);
    const plot = flatShape(points);
    plot.material = s.plot ? M.plotReal : M.plot;
    plot.position.y = .02;
    site.add(plot);
    const edge = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(p[0], .1, p[1]))), new THREE.LineDashedMaterial({ color: '#f0a35e', dashSize: 1.6, gapSize: 1 }));
    edge.computeLineDistances(); site.add(edge);
    if (s.plot) { loadImagery(s.plot); return; }
    if (wasReal) clearImagery();
    const side = Math.sqrt(s.area), h = side / 2;
    const road = new THREE.Mesh(new THREE.PlaneGeometry(1400, 11), M.road);
    road.rotation.x = -Math.PI / 2; road.position.set(0, .01, h + 8); road.receiveShadow = true; site.add(road);
    const road2 = new THREE.Mesh(new THREE.PlaneGeometry(9, 1400), M.road);
    road2.rotation.x = -Math.PI / 2; road2.position.set(h + 7, .012, 0); road2.receiveShadow = true; site.add(road2);
    /* Low neighbouring blocks, kept behind and beside the plot so the building stays the subject */
    for (let i = 0; i < 18; i++) {
      const a = seeded(i + 1), b = seeded(i + 40), c = seeded(i + 80);
      const w = 12 + a * 16, d = 11 + b * 14, ht = 5 + c * c * 14;
      const col = i % 6 - 2.5, row = Math.floor(i / 6);
      box(w, ht, d, M.neighbor, col * 34 + (a - .5) * 6, 0, -h - 20 - d / 2 - row * 34, site);
    }
    for (let i = 0; i < 6; i++) {
      const a = seeded(i + 120), c = seeded(i + 160);
      box(14 + a * 10, 5 + c * 9, 16, M.neighbor, -h - 22 - a * 6, 0, -14 + i * 22, site);
    }
    /* Trees line the left edge so they never stand in front of the building */
    for (let i = 0; i < 6; i++) tree(-h - 2.4, -h + i * side / 5, .85 + seeded(i) * .3, site);
  }

  /* Massing for each kind of investment */
  function buildMassing(s) {
    clear(building);
    clear(extras);
    const fit = footprintFor(s), { w, d, points } = fit;
    buildSite(s, points);
    /* The building turns to follow the plot's longest side */
    building.position.set(fit.center[0], 0, fit.center[1]);
    building.rotation.y = fit.rotation;
    if (w < 2.5 || d < 2.5) return 0;
    const floors = Math.max(1, Math.round(s.floors));

    if (s.program === 'villa') {
      const fh = 3.3;
      const cz = 0;
      let y = 0;
      for (let i = 0; i < floors; i++) {
        const shrink = i === 0 ? 1 : (i === 1 ? .78 : .55), fw = w * shrink, fd = d * (i === 0 ? 1 : .86);
        const fx = i === 0 ? 0 : -w * (1 - shrink) * .32, fz = cz + (i === 0 ? 0 : d * .05);
        box(fw - .4, fh - .3, fd - .4, M.glass, fx, y, fz);
        box(fw + .6, .3, fd + 1.2, M.plaster, fx, y + fh - .3, fz);
        box(Math.max(.9, fw * .22), fh - .3, fd * .9, i % 2 ? M.wood : M.plaster, fx + fw * .36, y, fz);
        y += fh;
      }
      /* The garden fills the plot, with a pool in front of the house when there is room */
      const g = flatShape(points);
      g.material = M.garden;
      g.position.y = .04;
      extras.add(g);
      for (const scale of [1, .75, .5]) {
        const pd = 5 * scale, pw = Math.min(w * .75, 12) * scale, pz = d / 2 + pd / 2 + 1.1;
        if (!localRectInPlot(points, fit, 0, pz, pw, pd)) continue;
        const p = new THREE.Mesh(new THREE.PlaneGeometry(pw, pd), M.water);
        p.rotation.x = -Math.PI / 2; p.position.set(0, .07, pz); building.add(p);
        break;
      }
      return y;
    }

    const groundH = 4.6, fh = 3.15;
    const cx = 0, cz = 0;
    let y = 0;
    /* Open ground floor, the shop or lobby level */
    box(w - 1, groundH - .4, d - 1, M.glass, cx, y, cz);
    box(w + .3, .4, d + .3, M.plaster, cx, y + groundH - .4, cz);
    y += groundH;
    const upper = floors - 1;
    for (let i = 0; i < upper; i++) {
      const stepped = s.program === 'hotel' ? Math.max(.42, 1 - (Math.max(0, i - Math.floor(upper * .3)) / Math.max(1, upper)) * .55) : 1;
      const fw = w * stepped;
      const fx = s.program === 'hotel' ? -(w - fw) * .5 : 0;
      const over = s.program === 'hotel' ? 1 : .85;
      const wave = s.program === 'apartments' ? Math.sin(i * .9) * .55 : 0;
      box(fw - .6, fh - .32, d - .7, M.glass, fx, y, cz);
      box(fw + over * 1.5 + wave, .32, d + over + wave, M.plaster, fx, y + fh - .32, cz);
      /* Vertical fins that give the facade rhythm */
      const fins = Math.max(3, Math.floor(fw / 4));
      for (let f = 0; f <= fins; f++) {
        const fxx = fx - fw / 2 + .35 + f * ((fw - .7) / fins);
        box(.22, fh - .32, .4, M.plaster, fxx, y, d / 2 - .22);
      }
      const sideFins = Math.max(2, Math.floor(d / 4));
      for (let f = 0; f <= sideFins; f++) {
        box(.4, fh - .32, .22, M.plaster, fx + fw / 2 - .22, y, -d / 2 + .35 + f * ((d - .7) / sideFins));
      }
      y += fh;
    }
    box(w * (s.program === 'hotel' ? .42 : .3), 2.3, d * .4, M.plaster, s.program === 'hotel' ? -w * .29 : 0, y, 0);
    /* Trees in the free part of the plot */
    return y + 2.3;
  }

  /* Sun, sky and window light */
  function applyLight(a, b, t) {
    mix(a.top, b.top, t, skyUniforms.top.value);
    mix(a.low, b.low, t, skyUniforms.low.value);
    scene.fog.color.copy(skyUniforms.low.value);
    mix(a.sun, b.sun, t, sun.color);
    sun.intensity = THREE.MathUtils.lerp(a.power, b.power, t);
    hemi.intensity = THREE.MathUtils.lerp(a.hemi, b.hemi, t);
    hemi.color.copy(skyUniforms.top.value).lerp(new THREE.Color('#ffffff'), .35);
    const glow = THREE.MathUtils.lerp(a.glow, b.glow, t);
    M.glass.emissiveIntensity = glow * 1.15;
    M.water.emissiveIntensity = glow * .55;
  }
  let sunReach = 340;
  /* The home page teaser has no date or place, so it keeps a simple day arc */
  function setHour(h) {
    applyLight(...hourStops(h));
    const p = (Math.max(6, Math.min(20.2, h)) - 6) / 14.2;
    const az = THREE.MathUtils.lerp(-1.75, 1.75, p), el = Math.sin(p * Math.PI) * 1.02 + .05;
    sun.position.set(Math.sin(az) * Math.cos(el) * 340, Math.sin(el) * 340, Math.cos(az) * Math.cos(el) * 340 * .9 + 40);
  }
  /* The real sun: azimuth clockwise from north, with north along -z */
  function setSun({ altitude, azimuth }) {
    const az = azimuth * Math.PI / 180, afternoon = Math.sin(az) < 0;
    applyLight(...altitudeStops(altitude, afternoon ? SETTING : RISING));
    sun.intensity *= THREE.MathUtils.smoothstep(altitude, -1, 2);
    const el = Math.max(altitude, 1) * Math.PI / 180;
    sun.position.set(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)).multiplyScalar(sunReach);
  }

  /* Camera follows the size of the project */
  const target = new THREE.Vector3(), camGoal = { dist: 150 };
  let controls = null, dist = 150;
  if (opts.controls !== false) {
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.dampingFactor = .07;
    controls.enablePan = false; controls.maxPolarAngle = Math.PI * .485; controls.minPolarAngle = .35;
    controls.minDistance = 30; controls.maxDistance = 480;
  }
  const baseFar = camera.far;
  let state = null, height = 10, autoSpin = opts.spin || 0, angle = opts.angle ?? .72;
  function setState(next) {
    const changed = !state || ['program', 'area', 'cover', 'floors', 'plot'].some(k => state[k] !== next[k]);
    const plotChanged = state && state.plot !== next.plot;
    state = { ...next };
    if (changed) {
      height = buildMassing(state);
      const { points } = footprintFor(state);
      const span = plotSpan(points);
      /* A real plot has no filler around it, so the camera can come closer */
      const cover = Math.max(span * (state.plot ? 1.35 : 2.15), height * 2.5, 38);
      camGoal.dist = cover * (opts.zoom || 1.4);
      camGoal.y = height * .42;
      if (plotChanged && controls) controls.userZoomed = false;
      /* Large plots need the camera, sky, ground and shadows to reach further */
      const edge = state.plot ? imageryRadius(span, state.plot.lat0) : 0;
      const world = Math.max(1, Math.max(camGoal.dist * 2.4, edge * 1.3) / 900);
      sky.scale.setScalar(world); ground.scale.setScalar(world);
      /* The imagery fades into the horizon before it ends */
      scene.fog.far = state.plot ? edge * .9 : 860 * world;
      scene.fog.near = state.plot ? Math.max(edge * .4, camGoal.dist * 1.15) : 300 * world;
      camera.far = baseFar * world; camera.near = Math.max(1, camGoal.dist * .02); camera.updateProjectionMatrix();
      if (controls) controls.maxDistance = Math.max(480, camGoal.dist * (state.plot ? 1.5 : 2));
      const shadow = Math.max(span, height) * 1.9 + 30, c = sun.shadow.camera;
      sunReach = Math.max(340, shadow * 1.3);
      c.left = -shadow; c.right = shadow; c.top = shadow; c.bottom = -shadow; c.near = 10; c.far = sunReach * 2.7; c.updateProjectionMatrix();
    }
    if (state.sun) setSun(state.sun); else setHour(state.hour);
    kick();
  }

  function size() {
    const r = host.getBoundingClientRect();
    const w = Math.max(1, r.width), h = Math.max(1, r.height);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    camera.setViewOffset(w, h, opts.offsetX ? opts.offsetX(w) : 0, 0, w, h);
    kick();
  }
  const ro = new ResizeObserver(size);
  ro.observe(host);

  const look = new THREE.Vector3();
  let running = true, visible = true, raf = 0, last = 0;
  function kick() { if (!raf && visible) raf = requestAnimationFrame(loop); }
  function loop(now) {
    raf = 0;
    if (!visible || !running) return;
    const dt = Math.min(.05, (now - last) / 1000 || 0); last = now;
    target.y += ((camGoal.y || 8) - target.y) * .07;
    dist += (camGoal.dist - dist) * .07;
    if (controls) {
      /* Keep the user's angle while easing distance to fit the building */
      const off = camera.position.clone().sub(controls.target);
      controls.target.copy(target);
      if (Math.abs(off.length() - camGoal.dist) > .5 && !controls.userZoomed) {
        off.setLength(off.length() + (camGoal.dist - off.length()) * .07);
      }
      camera.position.copy(target).add(off);
      controls.update();
    } else {
      angle += autoSpin * dt;
      camera.position.set(Math.sin(angle) * dist, target.y + dist * .27, Math.cos(angle) * dist);
      camera.lookAt(target);
    }
    renderer.render(scene, camera);
    if (opts.onBearing) { camera.getWorldDirection(look); opts.onBearing(Math.atan2(look.x, -look.z)); }
    const settling = Math.abs(dist - camGoal.dist) > .05 || Math.abs(target.y - (camGoal.y || 8)) > .02;
    if (autoSpin || settling || controls) raf = requestAnimationFrame(loop);
  }
  if (controls) {
    renderer.domElement.addEventListener('wheel', () => { controls.userZoomed = true; }, { passive: true });
  }
  new IntersectionObserver(es => {
    visible = es.some(e => e.isIntersecting);
    if (visible) { last = performance.now(); kick(); }
  }).observe(host);

  camera.position.set(Math.sin(angle) * 150, 44, Math.cos(angle) * 150);
  size();
  return { setState, renderer, get state() { return state; } };
}

/* Home page teaser: the building grows and the day passes as you scroll */
export function mountTeaser(el) {
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;inset:0;z-index:-1';
  el.prepend(host);
  const s = createScene(host, { controls: false, spin: .05, angle: .8, zoom: 1.75 });
  const chip = el.querySelector('.sun-chip b');
  const fmt = h => `${String(Math.floor(h)).padStart(2, '0')}:${String(Math.floor((h % 1) * 60)).padStart(2, '0')}`;
  const apply = p => {
    const hour = 9 + p * 12;
    s.setState({ program: 'apartments', area: 1500, cover: 50, floors: Math.round(3 + p * 11), hour });
    if (chip) chip.textContent = fmt(hour);
  };
  apply(0);
  if (window.gsap && window.ScrollTrigger && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    ScrollTrigger.create({ trigger: el, start: 'top 75%', end: 'bottom 35%', scrub: true, onUpdate: t => apply(t.progress) });
  } else apply(.8);
}

/* The full Plot Lab page */
const SAMPLE_PLACE = { lat: 35.7595, lng: -5.834, tz: 'Africa/Casablanca' };
const ZONE_LOOKUP = 'https://cdn.jsdelivr.net/npm/tz-lookup@6.1.25/+esm';

export function mountLab(root) {
  const I = window.MMA_I18N.lab;
  const $ = s => root.querySelector(s);
  const inputs = { area: $('#labArea'), cover: $('#labCover'), floors: $('#labFloors'), hour: $('#labHour'), day: $('#labDay') };
  const LIMITS = {
    villa: { area: [200, 1500, 600], cover: [20, 50, 35], floors: [1, 3, 2] },
    apartments: { area: [200, 3500, 900], cover: [30, 80, 60], floors: [2, 16, 7] },
    hotel: { area: [500, 5000, 2400], cover: [25, 70, 40], floors: [2, 10, 5] }
  };
  const RATES = I.rates;
  const YEAR = new Date().getFullYear();
  const yearDays = dayOfYear(new Date(YEAR, 11, 31));
  /* A date that has already passed this year means its next occurrence, since the building is still to come */
  const today = dayOfYear();
  const yearOf = day => (day < today ? YEAR + 1 : YEAR);
  const state = { program: 'apartments', finish: 'standard', hour: 15.5, day: dayOfYear(), area: 900, cover: 60, floors: 7, plot: null, sun: null };
  let place = { ...SAMPLE_PLACE };
  const q = new URLSearchParams(location.search);
  if (LIMITS[q.get('p')]) {
    state.program = q.get('p');
    Object.assign(state, { area: +q.get('a') || LIMITS[state.program].area[2], cover: +q.get('c') || LIMITS[state.program].cover[2], floors: +q.get('f') || LIMITS[state.program].floors[2] });
    if (RATES[q.get('finish')]) state.finish = q.get('finish');
    if (+q.get('h')) state.hour = +q.get('h');
    if (+q.get('d') >= 1 && +q.get('d') <= yearDays) state.day = Math.round(+q.get('d'));
  }

  /* The compass turns with the camera */
  const needle = $('.lab-compass i');
  let shownBearing = 1e9;
  const onBearing = b => {
    if (Math.abs(b - shownBearing) < .003) return;
    shownBearing = b;
    needle.style.transform = `rotate(${-b}rad)`;
  };

  let scene = null;
  try {
    scene = createScene($('.lab-canvas'), { offsetX: w => (w > 1040 ? Math.min(w * .13, 200) * (document.documentElement.dir === 'rtl' ? -1 : 1) : 0), zoom: 2, imageryUrl: I.map.imagery, onBearing });
  } catch (e) {
    $('.lab-canvas').innerHTML = `<p class="lab-hint">${I.noGl}</p>`;
  }

  const loc = I.locale;
  const fmt = n => Math.round(n).toLocaleString(loc);
  const money = n => fmt(Math.round(n / 1e4) * 1e4);
  const hourTxt = h => { const m = Math.round(h * 60) % 1440; return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };
  const levelCode = f => (f === 1 ? I.ground : `${I.ground}+${f - 1}`);
  const levels = f => (I.levelsText ? I.levelsText.replace('{n}', f) : levelCode(f));
  /* Counted nouns: the forms come from the page's language, which for Arabic has more than singular and plural */
  const plural = new Intl.PluralRules(document.documentElement.lang);
  const counted = (forms, n) => (forms[plural.select(n)] || forms.other).replace('{n}', fmt(n));
  const dateTxt = day => new Date(Date.UTC(yearOf(day), 0, day)).toLocaleDateString(I.dateLocale, { day: 'numeric', month: 'long', timeZone: 'UTC' });

  function calc(s = state) {
    const fit = footprintFor(s), wanted = s.area * s.cover / 100;
    const fp = Math.min(fit.area, wanted), total = fp * s.floors;
    const [lo, hi] = RATES[s.finish];
    const buildLo = total * lo, buildHi = total * hi;
    const budgetLo = buildLo * (1 + .06 + .1), budgetHi = buildHi * (1 + .12 + .1);
    let cap = '';
    if (s.program === 'apartments') cap = counted(I.units, Math.floor(total * .8 / 85));
    else if (s.program === 'hotel') cap = counted(I.rooms, Math.floor(total * .6 / 40));
    else cap = I.oneVilla;
    return { fp, total, cap, budgetLo, budgetHi, limited: fp < wanted * .99 };
  }
  function shareUrl() {
    const u = new URL(location.href);
    u.search = new URLSearchParams({ p: state.program, a: state.area, c: state.cover, f: state.floors, h: state.hour, d: state.day, finish: state.finish }).toString();
    /* The plot stays in the hash, so its location is never sent to our server just by opening a link */
    u.hash = state.plot ? `plot=${state.plot.key}` : '';
    return u.href;
  }

  /* Sunrise and sunset are worked out once per place and day, then set the range of the time slider */
  let timesKey = '', times = null;
  function dayTimes() {
    const key = `${place.lat},${place.lng},${place.tz},${state.day}`;
    if (key !== timesKey) { timesKey = key; times = sunTimes(yearOf(state.day), state.day, place); }
    return times;
  }
  function updateSun() {
    const { rise, set } = dayTimes();
    const min = rise === null ? 0 : Math.max(0, Math.floor((rise - .75) * 4) / 4);
    const max = set === null ? 24 : Math.min(24, Math.ceil((set + .75) * 4) / 4);
    inputs.hour.min = min; inputs.hour.max = max;
    state.hour = Math.max(min, Math.min(max, state.hour));
    state.sun = sunPosition(clockToDate(yearOf(state.day), state.day, state.hour, place), place.lat, place.lng);
  }

  function render() {
    updateSun();
    Object.keys(inputs).forEach(k => { inputs[k].value = state[k]; });
    const c = calc();
    $('#outArea').textContent = `${fmt(state.area)} ${I.m2}`;
    $('#outCover').textContent = `${state.cover} %`;
    $('#outFloors').textContent = levels(state.floors);
    $('#outHour').textContent = hourTxt(state.hour);
    $('#outDay').textContent = dateTxt(state.day);
    $('#resFloor').textContent = `${fmt(c.total)} ${I.m2}`;
    $('#resCap').textContent = c.cap;
    $('#resBudget').textContent = `${money(c.budgetLo)} – ${money(c.budgetHi)} ${I.mad}`;
    root.querySelectorAll('[data-program]').forEach(b => b.setAttribute('aria-pressed', b.dataset.program === state.program));
    root.querySelectorAll('[data-finish]').forEach(b => b.setAttribute('aria-pressed', b.dataset.finish === state.finish));

    /* Plot summary */
    const real = !!state.plot;
    $('#plotLabel').textContent = real ? I.plotYours : I.plotSample;
    const detail = $('#plotDetail');
    detail.textContent = real ? `${fmt(state.area)} ${I.m2} · ` : I.plotSampleNote;
    if (real) {
      /* Coordinates keep their reading order inside Arabic text */
      const coords = document.createElement('bdi');
      coords.dir = 'ltr';
      coords.textContent = `${state.plot.lat0.toFixed(5)}, ${state.plot.lng0.toFixed(5)}`;
      detail.append(coords);
    }
    $('#plotPick').textContent = real ? I.plotChange : I.plotPick;
    $('#plotReset').classList.toggle('hide', !real);
    $('#labAreaCtl').classList.toggle('hide', real);
    $('.lab-credit').classList.toggle('hide', !real);
    const fitNote = $('#labFitNote');
    fitNote.classList.toggle('hide', !c.limited);
    if (c.limited) fitNote.textContent = I.fitLimit.replace('{pct}', Math.round(c.fp / state.area * 100));

    /* Sun summary */
    const { rise, set } = dayTimes(), sun = state.sun;
    const zone = `${place.tz ? '' : '≈ '}${offsetLabel(yearOf(state.day), state.day, place)}`;
    $('#outSunTimes').textContent = rise === null || set === null
      ? `${I.noRiseSet} · ${zone}`
      : `${I.sunrise} ${hourTxt(rise)} · ${I.sunset} ${hourTxt(set)} · ${zone}`;
    $('#outSunNow').textContent = sun.altitude > 0
      ? I.sunNow.replace('{alt}', Math.round(sun.altitude)).replace('{az}', Math.round(sun.azimuth))
      : I.sunBelow;

    if (scene) scene.setState(state);
    const type = { villa: 'home', apartments: 'rental', hotel: 'hospitality' }[state.program];
    let study = `${fmt(state.area)} ${I.m2}, ${state.cover} %, ${levelCode(state.floors)}, ${fmt(c.total)} ${I.m2}`;
    if (real) study += ` · ${I.studyPlot}: ${state.plot.lat0.toFixed(5)}, ${state.plot.lng0.toFixed(5)} · ${shareUrl()}`;
    $('#labSend').href = `${I.contactUrl}?type=${type}#study=${encodeURIComponent(study)}`;
  }
  function setLimits() {
    const L = LIMITS[state.program];
    ['area', 'cover', 'floors'].forEach(k => {
      inputs[k].min = L[k][0]; inputs[k].max = L[k][1];
      /* A drawn plot's area is measured, so the sample limits don't apply to it */
      if (k === 'area' && state.plot) return;
      state[k] = Math.max(L[k][0], Math.min(L[k][1], state[k]));
    });
  }

  /* The clock at the plot depends on its time zone, found from its coordinates */
  let zoneLookup = null;
  const loadZones = () => {
    zoneLookup = zoneLookup || import(ZONE_LOOKUP).then(m => m.default).catch(() => { zoneLookup = null; return null; });
    return zoneLookup;
  };
  async function findZone(target) {
    const lookup = await loadZones();
    if (!lookup || target !== place) return;
    try {
      const tz = lookup(target.lat, target.lng);
      new Intl.DateTimeFormat('en', { timeZone: tz });
      target.tz = tz;
      render();
    } catch (e) { /* Keep the estimate from longitude, which the page marks with ≈ */ }
  }

  function applyPlot(latLngs) {
    if (latLngs) {
      const { points, lat0, lng0 } = toLocal(latLngs);
      state.plot = { latLngs, points, lat0, lng0, key: encodePlot(latLngs) };
      state.area = Math.round(polygonArea(points));
      place = { lat: lat0, lng: lng0, tz: null };
      findZone(place);
    } else {
      state.plot = null;
      state.area = LIMITS[state.program].area[2];
      place = { ...SAMPLE_PLACE };
    }
    setLimits();
    render();
  }

  ['area', 'cover', 'floors', 'hour', 'day'].forEach(k => inputs[k].addEventListener('input', () => { state[k] = Number(inputs[k].value); render(); }));
  root.querySelectorAll('[data-program]').forEach(b => b.addEventListener('click', () => {
    state.program = b.dataset.program;
    const L = LIMITS[state.program];
    if (!state.plot) state.area = L.area[2];
    state.cover = L.cover[2]; state.floors = L.floors[2];
    setLimits(); render();
  }));
  root.querySelectorAll('[data-finish]').forEach(b => b.addEventListener('click', () => { state.finish = b.dataset.finish; render(); }));

  /* Date shortcuts */
  inputs.day.max = yearDays;
  const dayShortcuts = { today: dayOfYear(), june: dayOfYear(new Date(YEAR, 5, 21)), december: dayOfYear(new Date(YEAR, 11, 21)) };
  root.querySelectorAll('[data-day]').forEach(b => {
    const day = dayShortcuts[b.dataset.day];
    if (b.dataset.day !== 'today') b.textContent = dateTxt(day);
    b.addEventListener('click', () => { state.day = day; render(); });
  });

  /* Finding and drawing the plot */
  $('#plotPick').addEventListener('click', async () => {
    const btn = $('#plotPick');
    btn.disabled = true;
    loadZones();
    try {
      const { openPlotPicker } = await import('./plot-map.js');
      const latLngs = await openPlotPicker({ I: I.map, locale: I.locale, initial: state.plot && state.plot.latLngs, centre: [place.lat, place.lng] });
      if (latLngs) applyPlot(latLngs);
    } catch (e) {
      $('#plotDetail').textContent = I.map.loadFail;
    }
    btn.disabled = false;
  });
  $('#plotReset').addEventListener('click', () => applyPlot(null));

  /* Press and hold the sun button to play a full day */
  let play = 0;
  $('#labPlay').addEventListener('click', () => {
    if (play) { cancelAnimationFrame(play); play = 0; $('#labPlay').textContent = I.play; return; }
    $('#labPlay').textContent = I.pause;
    if (state.hour >= +inputs.hour.max - .1) state.hour = +inputs.hour.min;
    const step = () => {
      const end = +inputs.hour.max;
      state.hour = Math.min(end, state.hour + .035);
      render();
      if (state.hour >= end) { play = 0; $('#labPlay').textContent = I.play; return; }
      play = requestAnimationFrame(step);
    };
    play = requestAnimationFrame(step);
  });

  /* Copy a link to this exact study */
  $('#labShare').addEventListener('click', async () => {
    const btn = $('#labShare'), done = () => { btn.textContent = I.copied; setTimeout(() => { btn.textContent = I.share; }, 1800); };
    try { await navigator.clipboard.writeText(shareUrl()); done(); }
    catch (e) { history.replaceState(null, '', shareUrl()); btn.textContent = I.linkInBar; setTimeout(() => { btn.textContent = I.share; }, 2400); }
  });

  /* Save up to three options and compare them */
  const saved = [];
  const compareBox = document.getElementById('labCompare');
  function drawSaved() {
    compareBox.classList.toggle('hide', !saved.length);
    const body = document.getElementById('labCompareBody');
    body.textContent = '';
    saved.forEach((o, i) => {
      const c = calc(o), tr = document.createElement('tr');
      [`${I.option} ${String.fromCharCode(65 + i)}`, I.programs[o.program], `${fmt(o.area)} ${I.m2}`, `${Math.round(c.fp / o.area * 100)} %`, levels(o.floors), `${fmt(c.total)} ${I.m2}`, c.cap, I.finishes[o.finish], `${money(c.budgetLo)} – ${money(c.budgetHi)}`].forEach(t => {
        const td = document.createElement('td'); td.textContent = t; tr.append(td);
      });
      const td = document.createElement('td'), del = document.createElement('button');
      del.type = 'button'; del.className = 'link'; del.textContent = I.remove;
      del.addEventListener('click', () => { saved.splice(i, 1); drawSaved(); });
      td.append(del); tr.append(td); body.append(tr);
    });
    if (window.ScrollTrigger) ScrollTrigger.refresh();
  }
  $('#labSave').addEventListener('click', () => {
    if (saved.length === 3) saved.shift();
    saved.push({ ...state });
    drawSaved();
    const btn = $('#labSave');
    btn.textContent = `${I.saved} (${saved.length}/3)`;
    setTimeout(() => { btn.textContent = I.save; }, 1500);
  });

  setLimits();
  applyPlot(decodePlot(new URLSearchParams(location.hash.slice(1)).get('plot')));
}
