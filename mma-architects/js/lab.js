/* Plot Lab: a live 3D massing model with a moving sun. */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

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
  ground.position.y = -.06;
  ground.receiveShadow = true;
  scene.add(ground);

  const site = new THREE.Group(), building = new THREE.Group();
  scene.add(site, building);

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

  /* The plot, road, neighbours and planting scale with the plot */
  let lastSide = 0;
  function buildSite(side) {
    if (Math.abs(side - lastSide) < .01) return;
    lastSide = side;
    clear(site);
    const h = side / 2;
    const plot = new THREE.Mesh(new THREE.PlaneGeometry(side, side), M.plot);
    plot.rotation.x = -Math.PI / 2; plot.position.y = .02; plot.receiveShadow = true; site.add(plot);
    const edge = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-h, .1, -h), new THREE.Vector3(h, .1, -h), new THREE.Vector3(h, .1, h), new THREE.Vector3(-h, .1, h)
    ]), new THREE.LineDashedMaterial({ color: '#f0a35e', dashSize: 1.6, gapSize: 1 }));
    edge.computeLineDistances(); site.add(edge);
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
    const side = Math.sqrt(s.area), fp = s.area * s.cover / 100;
    const ratio = s.program === 'apartments' ? 1.4 : s.program === 'hotel' ? 1.6 : 1.3;
    const w = Math.min(Math.sqrt(fp * ratio), side), d = Math.min(fp / w, side);
    buildSite(side);
    const floors = Math.max(1, Math.round(s.floors));

    if (s.program === 'villa') {
      const fh = 3.3;
      const offsetZ = (side - d) / 2 - Math.min(side * .12, 3);
      const cz = -offsetZ * .55;
      let y = 0;
      for (let i = 0; i < floors; i++) {
        const shrink = i === 0 ? 1 : (i === 1 ? .78 : .55), fw = w * shrink, fd = d * (i === 0 ? 1 : .86);
        const fx = i === 0 ? 0 : -w * (1 - shrink) * .32, fz = cz + (i === 0 ? 0 : d * .05);
        box(fw - .4, fh - .3, fd - .4, M.glass, fx, y, fz);
        box(fw + .6, .3, fd + 1.2, M.plaster, fx, y + fh - .3, fz);
        box(Math.max(.9, fw * .22), fh - .3, fd * .9, i % 2 ? M.wood : M.plaster, fx + fw * .36, y, fz);
        y += fh;
      }
      /* Pool and garden in the open part of the plot */
      const open = side / 2 - (cz + d / 2);
      if (open > 4) {
        const gardenD = open - .5;
        const g = new THREE.Mesh(new THREE.PlaneGeometry(side - 1, gardenD), M.garden);
        g.rotation.x = -Math.PI / 2; g.position.set(0, .04, side / 2 - gardenD / 2 - .25); g.receiveShadow = true; building.add(g);
        const pd = Math.min(gardenD * .45, 5), pw = Math.min(w * .75, 12);
        const p = new THREE.Mesh(new THREE.PlaneGeometry(pw, pd), M.water);
        p.rotation.x = -Math.PI / 2; p.position.set(0, .07, cz + d / 2 + pd / 2 + 1.1); building.add(p);
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
  function setHour(h) {
    const [a, b, t] = hourStops(h);
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
    const p = (Math.max(6, Math.min(20.2, h)) - 6) / 14.2;
    const az = THREE.MathUtils.lerp(-1.75, 1.75, p), el = Math.sin(p * Math.PI) * 1.02 + .05;
    const R = 340;
    sun.position.set(Math.sin(az) * Math.cos(el) * R, Math.sin(el) * R, Math.cos(az) * Math.cos(el) * R * .9 + 40);
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
  let state = null, height = 10, autoSpin = opts.spin || 0, angle = opts.angle ?? .72;
  function setState(next) {
    const changed = !state || ['program', 'area', 'cover', 'floors'].some(k => state[k] !== next[k]);
    state = { ...next };
    if (changed) {
      height = buildMassing(state);
      const side = Math.sqrt(state.area);
      const cover = Math.max(side * 2.15, height * 2.5, 38);
      camGoal.dist = cover * (opts.zoom || 1.4);
      camGoal.y = height * .42;
      const shadow = Math.max(side, height) * 1.9 + 30, c = sun.shadow.camera;
      c.left = -shadow; c.right = shadow; c.top = shadow; c.bottom = -shadow; c.near = 10; c.far = 900; c.updateProjectionMatrix();
    }
    setHour(state.hour);
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
export function mountLab(root) {
  const I = window.MMA_I18N.lab;
  const $ = s => root.querySelector(s);
  const inputs = { area: $('#labArea'), cover: $('#labCover'), floors: $('#labFloors'), hour: $('#labHour') };
  const LIMITS = {
    villa: { area: [200, 1500, 600], cover: [20, 50, 35], floors: [1, 3, 2] },
    apartments: { area: [200, 3500, 900], cover: [30, 80, 60], floors: [2, 16, 7] },
    hotel: { area: [500, 5000, 2400], cover: [25, 70, 40], floors: [2, 10, 5] }
  };
  const RATES = I.rates;
  const state = { program: 'apartments', finish: 'standard', hour: 15.5, area: 900, cover: 60, floors: 7 };
  const q = new URLSearchParams(location.search);
  if (LIMITS[q.get('p')]) {
    state.program = q.get('p');
    Object.assign(state, { area: +q.get('a') || LIMITS[state.program].area[2], cover: +q.get('c') || LIMITS[state.program].cover[2], floors: +q.get('f') || LIMITS[state.program].floors[2] });
    if (RATES[q.get('finish')]) state.finish = q.get('finish');
    if (+q.get('h')) state.hour = +q.get('h');
  }

  let scene = null;
  try {
    scene = createScene($('.lab-canvas'), { offsetX: w => (w > 1040 ? Math.min(w * .13, 200) : 0), zoom: 2 });
  } catch (e) {
    $('.lab-canvas').innerHTML = `<p class="lab-hint">${I.noGl}</p>`;
  }

  const loc = document.documentElement.lang === 'fr' ? 'fr-FR' : 'en-GB';
  const fmt = n => Math.round(n).toLocaleString(loc);
  const money = n => fmt(Math.round(n / 1e4) * 1e4);
  const hourTxt = h => `${String(Math.floor(h)).padStart(2, '0')}:${String(Math.round((h % 1) * 60)).padStart(2, '0')}`;
  const levels = f => (f === 1 ? I.ground : `${I.ground}+${f - 1}`);

  function calc(s = state) {
    const fp = s.area * s.cover / 100, total = fp * s.floors;
    const [lo, hi] = RATES[s.finish];
    const buildLo = total * lo, buildHi = total * hi;
    const budgetLo = buildLo * (1 + .06 + .1), budgetHi = buildHi * (1 + .12 + .1);
    let cap = '';
    if (s.program === 'apartments') cap = `${fmt(Math.floor(total * .8 / 85))} ${I.units}`;
    else if (s.program === 'hotel') cap = `${fmt(Math.floor(total * .6 / 40))} ${I.rooms}`;
    else cap = I.oneVilla;
    return { fp, total, cap, budgetLo, budgetHi };
  }
  function shareUrl() {
    const u = new URL(location.href);
    u.search = new URLSearchParams({ p: state.program, a: state.area, c: state.cover, f: state.floors, h: state.hour, finish: state.finish }).toString();
    return u.href;
  }
  function render() {
    Object.keys(inputs).forEach(k => { inputs[k].value = state[k]; });
    const c = calc();
    $('#outArea').textContent = `${fmt(state.area)} m²`;
    $('#outCover').textContent = `${state.cover} %`;
    $('#outFloors').textContent = levels(state.floors);
    $('#outHour').textContent = hourTxt(state.hour);
    $('#resFloor').textContent = `${fmt(c.total)} m²`;
    $('#resCap').textContent = c.cap;
    $('#resBudget').textContent = `${money(c.budgetLo)} – ${money(c.budgetHi)} MAD`;
    root.querySelectorAll('[data-program]').forEach(b => b.setAttribute('aria-pressed', b.dataset.program === state.program));
    root.querySelectorAll('[data-finish]').forEach(b => b.setAttribute('aria-pressed', b.dataset.finish === state.finish));
    if (scene) scene.setState(state);
    const type = { villa: 'home', apartments: 'rental', hotel: 'hospitality' }[state.program];
    const study = `${fmt(state.area)} m², ${state.cover} %, ${levels(state.floors)}, ${fmt(c.total)} m²`;
    $('#labSend').href = `${I.contactUrl}?type=${type}&study=${encodeURIComponent(study)}`;
  }
  function setLimits() {
    const L = LIMITS[state.program];
    ['area', 'cover', 'floors'].forEach(k => {
      inputs[k].min = L[k][0]; inputs[k].max = L[k][1];
      state[k] = Math.max(L[k][0], Math.min(L[k][1], state[k]));
    });
  }
  ['area', 'cover', 'floors', 'hour'].forEach(k => inputs[k].addEventListener('input', () => { state[k] = Number(inputs[k].value); render(); }));
  root.querySelectorAll('[data-program]').forEach(b => b.addEventListener('click', () => {
    state.program = b.dataset.program;
    const L = LIMITS[state.program];
    state.area = L.area[2]; state.cover = L.cover[2]; state.floors = L.floors[2];
    setLimits(); render();
  }));
  root.querySelectorAll('[data-finish]').forEach(b => b.addEventListener('click', () => { state.finish = b.dataset.finish; render(); }));

  /* Press and hold the sun button to play a full day */
  let play = 0;
  $('#labPlay').addEventListener('click', () => {
    if (play) { cancelAnimationFrame(play); play = 0; $('#labPlay').textContent = I.play; return; }
    $('#labPlay').textContent = I.pause;
    if (state.hour >= 20.9) state.hour = 6;
    const step = () => {
      state.hour = Math.min(21, state.hour + .035);
      render();
      if (state.hour >= 21) { play = 0; $('#labPlay').textContent = I.play; return; }
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
      [`${I.option} ${String.fromCharCode(65 + i)}`, I.programs[o.program], `${fmt(o.area)} m²`, `${o.cover} %`, levels(o.floors), `${fmt(c.total)} m²`, c.cap, I.finishes[o.finish], `${money(c.budgetLo)} – ${money(c.budgetHi)}`].forEach(t => {
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
  render();
}
