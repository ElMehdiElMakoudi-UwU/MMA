/* Shared motion and interactions. Every effect has a usable state without it. */
(function () {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGsap = !!(window.gsap && window.ScrollTrigger);
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const wide = () => innerWidth > 720;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const motion = hasGsap && !reduce;
  if (!motion) root.classList.add('no-motion');

  /* Smooth scrolling */
  let lenis = null;
  if (motion && window.Lenis && fine) {
    lenis = new Lenis({ duration: 1.05, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
    window.MMA_LENIS = lenis;
  }

  /* Header */
  const head = $('.head');
  let lastY = 0;
  const onScroll = () => {
    const y = scrollY;
    head.classList.toggle('scrolled', y > 40);
    head.classList.toggle('hidden', y > lastY && y > 500 && !root.classList.contains('menu-open'));
    lastY = y;
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  const menuBtn = $('.menu-btn');
  if (menuBtn) menuBtn.addEventListener('click', () => {
    const open = root.classList.toggle('menu-open');
    menuBtn.setAttribute('aria-expanded', open);
    if (lenis) open ? lenis.stop() : lenis.start();
  });

  /* Floating contact */
  const dock = $('.dock');
  if (dock) {
    const btn = $('.dock-btn', dock);
    btn.addEventListener('click', () => {
      const open = dock.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
    document.addEventListener('click', e => { if (!dock.contains(e.target)) dock.classList.remove('open'); });
  }

  /* Page wipe between pages (internal links only) */
  const wipe = $('.wipe');
  if (wipe && motion && !document.startViewTransition) {
    document.addEventListener('click', e => {
      const a = e.target.closest('a[href]');
      if (!a || a.target || e.metaKey || e.ctrlKey || e.shiftKey) return;
      const href = a.getAttribute('href');
      if (!href || href.startsWith('#') || /^(tel:|mailto:|https?:)/.test(href)) return;
      e.preventDefault();
      gsap.fromTo(wipe, { clipPath: 'polygon(120% 0,120% 0,100% 100%,100% 100%)' },
        { clipPath: 'polygon(-20% 0,120% 0,100% 100%,-20% 100%)', duration: .6, ease: 'power3.inOut', onComplete: () => { location.href = a.href; } });
      gsap.to($('img', wipe), { opacity: 1, duration: .3, delay: .25 });
    });
  }
  addEventListener('pageshow', e => {
    if (e.persisted && wipe) gsap && gsap.set(wipe, { clipPath: 'polygon(100% 0,100% 0,100% 100%,100% 100%)' });
  });

  /* Split headings into masked lines, once the real font has set the line breaks */
  function splitLines() {
    $$('[data-lines]').forEach(el => {
      const text = el.textContent.trim();
      el.setAttribute('aria-label', text);
      el.innerHTML = text.split(/\s+/).map(w => `<span class="w-m" aria-hidden="true" style="display:inline-block">${w}</span>`).join(' ');
      const lines = [];
      $$('.w-m', el).forEach(s => {
        const top = s.offsetTop, last = lines[lines.length - 1];
        if (last && Math.abs(last.top - top) < 6) last.words.push(s.textContent);
        else lines.push({ top, words: [s.textContent] });
      });
      el.innerHTML = lines.map(l => `<span class="line" aria-hidden="true"><span>${l.words.join(' ')}</span></span>`).join('');
      el.classList.add('split');
      if (!motion) return;
      const inHero = el.closest('.hero, .ph-hero, .page-head, .brief, .lab');
      gsap.to($$('.line>span', el), {
        y: 0, yPercent: 0, duration: 1.25, ease: 'expo.out', stagger: .1, delay: inHero ? .15 : 0,
        scrollTrigger: inHero ? null : { trigger: el, start: 'top 86%', once: true }
      });
    });
    if (motion) ScrollTrigger.refresh();
  }
  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  Promise.race([fontsReady, new Promise(r => setTimeout(r, 1500))]).then(splitLines);

  const imageReveal = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    imageReveal.unobserve(e.target);
  }), { rootMargin: '0px 0px -8% 0px' });

  if (motion) {
    gsap.registerPlugin(ScrollTrigger);

    $$('[data-reveal]').forEach(el => {
      if (el.dataset.reveal === 'img') {
        /* A clipped image never enters the viewport for lazy loading, so fetch it up front */
        $$('img', el).forEach(i => { i.loading = 'eager'; });
        imageReveal.observe(el);
      } else {
        gsap.to(el, { opacity: 1, y: 0, duration: 1.05, ease: 'expo.out',
          delay: el.closest('.hero, .ph-hero, .page-head') ? .55 : 0,
          scrollTrigger: { trigger: el, start: 'top 92%', once: true } });
      }
    });
    $$('[data-parallax]').forEach(el => {
      gsap.fromTo(el, { yPercent: -Number(el.dataset.parallax) }, { yPercent: Number(el.dataset.parallax), ease: 'none',
        scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
    $$('[data-count]').forEach(el => {
      const end = Number(el.dataset.count), o = { v: 0 }, fmt = el.dataset.locale || 'en-GB', unit = el.dataset.unit || '';
      gsap.to(o, { v: end, duration: 2, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        onUpdate: () => { el.textContent = Math.round(o.v).toLocaleString(fmt) + unit; } });
    });

    /* Word-by-word statement */
    $$('.statement').forEach(el => {
      el.innerHTML = el.textContent.trim().split(/\s+/).map(w => `<span class="w">${w}</span>`).join(' ');
      gsap.to($$('.w', el), { opacity: 1, stagger: .4, ease: 'none',
        scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 45%', scrub: .4 } });
    });

    /* Marquee */
    $$('.marquee-track').forEach(t => {
      t.innerHTML += t.innerHTML;
      const tween = gsap.to(t, { xPercent: -50, duration: 36, ease: 'none', repeat: -1 });
      ScrollTrigger.create({ onUpdate: s => {
        gsap.to(tween, { timeScale: 1 + Math.min(Math.abs(s.getVelocity()) / 700, 4), duration: .2, overwrite: true });
        gsap.to(tween, { timeScale: 1, duration: 1, delay: .25 });
      } });
    });

    /* Pinned plot story */
    const story = $('.story');
    if (story) {
      const frames = $$('.story-frames img', story), steps = $$('.story-step', story);
      const num = $('.story-num b', story), bars = $$('.story-progress i', story);
      const from = Number(num.dataset.from), to = Number(num.dataset.to), loc = num.dataset.locale;
      const n = steps.length;
      if (innerWidth > 1040) {
        ScrollTrigger.create({
          trigger: story, start: 'top top', end: () => '+=' + innerHeight * (n * .85), pin: '.story-pin', scrub: true, anticipatePin: 1,
          onUpdate: s => {
            const raw = s.progress * (n - .001), i = Math.floor(raw), f = raw - i;
            steps.forEach((st, k) => {
              const on = k === i;
              gsap.set(st, { opacity: on ? 1 : 0, y: on ? 0 : 14 });
            });
            frames.forEach((fr, k) => {
              let op = 0;
              if (k === i) op = 1;
              if (k === i + 1) op = Math.max(0, (f - .78) / .22);
              gsap.set(fr, { opacity: op, zIndex: k === i + 1 ? 2 : 1 });
            });
            const shrink = gsap.utils.clamp(0, 1, s.progress / .42);
            num.textContent = Math.round(from + (to - from) * gsap.parseEase('power2.inOut')(shrink)).toLocaleString(loc);
            bars.forEach((b, k) => b.style.setProperty('--p', gsap.utils.clamp(0, 1, raw - k)));
          }
        });
      } else {
        /* Phones step automatically as the section enters view, without pinning */
        let i = 0;
        const show = k => {
          steps.forEach((st, j) => gsap.to(st, { opacity: j === k ? 1 : 0, duration: .5 }));
          frames.forEach((fr, j) => gsap.to(fr, { opacity: j === k ? 1 : 0, duration: .7 }));
          bars.forEach((b, j) => b.style.setProperty('--p', j <= k ? 1 : 0));
          const v = k === 0 ? from : to;
          gsap.to({ v: Number(num.textContent.replace(/\D/g, '')) || from }, { v, duration: 1, onUpdate() { num.textContent = Math.round(this.targets()[0].v).toLocaleString(loc); } });
        };
        ScrollTrigger.create({ trigger: story, start: 'top 60%', once: true, onEnter: () => {
          show(0);
          setInterval(() => { i = (i + 1) % n; show(i); }, 3600);
        } });
      }
    }

    /* Horizontal rails */
    $$('[data-rail]').forEach(wrap => {
      const rail = $('.rail', wrap);
      if (!rail || !wide()) return;
      const dist = () => Math.max(0, rail.scrollWidth - innerWidth);
      gsap.to(rail, { x: () => -dist(), ease: 'none',
        scrollTrigger: { trigger: wrap, start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 1, invalidateOnRefresh: true, anticipatePin: 1 } });
    });
    const stages = $('.stages-pin');
    if (stages && wide()) {
      const tr = $('.stages-track', stages);
      const dist = () => Math.max(0, tr.scrollWidth - innerWidth);
      gsap.to(tr, { x: () => -dist(), ease: 'none',
        scrollTrigger: { trigger: stages, start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 1, invalidateOnRefresh: true } });
    }

    /* Day and night slider moves itself once to show it can be dragged */
    $$('.compare[data-tease]').forEach(c => {
      const o = { x: 78 };
      ScrollTrigger.create({ trigger: c, start: 'top 55%', once: true, onEnter: () => {
        if (c.dataset.touched) return;
        gsap.to(o, { x: 34, duration: 2, ease: 'power2.inOut', onUpdate: () => { if (!c.dataset.touched) setCompare(c, o.x); } });
      } });
      setCompare(c, 78);
    });

    addEventListener('load', () => ScrollTrigger.refresh());
  }

  /* Hero slideshow with diagonal wipe */
  const hero = $('.hero');
  if (hero) {
    const slides = $$('.hero-slide', hero), bars = $$('.hero-bars button', hero), caption = $('.hero-caption', hero);
    let cur = 0, timer = null, tween = null;
    const DUR = 6.5;
    const go = n => {
      if (n === cur) return;
      const prev = slides[cur], next = slides[n];
      slides.forEach(s => s.classList.remove('leaving', 'entering'));
      prev.classList.remove('on'); prev.classList.add('leaving');
      const im = $('img', next);
      im.style.animation = 'none'; void im.offsetWidth; im.style.animation = '';
      next.classList.add('entering');
      next.addEventListener('animationend', function done(e) {
        if (e.target !== next) return;
        next.removeEventListener('animationend', done);
        next.classList.remove('entering'); next.classList.add('on'); prev.classList.remove('leaving');
      });
      cur = n;
      caption.innerHTML = next.dataset.caption;
      progress();
    };
    const progress = () => {
      bars.forEach((b, i) => { const f = $('i', b); if (f) f.style.transform = `scaleX(${i < cur ? 1 : 0})`; });
      if (reduce || !window.gsap) return;
      if (tween) tween.kill();
      tween = gsap.fromTo($('i', bars[cur]), { scaleX: 0 }, { scaleX: 1, duration: DUR, ease: 'none', onComplete: () => go((cur + 1) % slides.length) });
    };
    bars.forEach((b, i) => b.addEventListener('click', () => go(i)));
    if (slides.length) { slides[0].classList.add('on'); caption.innerHTML = slides[0].dataset.caption; progress(); }
    /* Pointer parallax */
    if (fine && motion) hero.addEventListener('mousemove', e => {
      const x = (e.clientX / innerWidth - .5), y = (e.clientY / innerHeight - .5);
      gsap.to($$('.hero-slide img', hero), { x: x * -24, y: y * -16, duration: 1.4, ease: 'power3.out', overwrite: 'auto' });
    });
  }

  /* Day and night compare */
  function setCompare(c, pct) {
    c.style.setProperty('--x', pct + '%');
    const inp = $('input', c);
    if (inp) inp.value = pct;
  }
  $$('.compare').forEach(c => {
    const inp = $('input', c);
    if (inp) {
      inp.addEventListener('input', () => { c.dataset.touched = '1'; setCompare(c, Number(inp.value)); });
      inp.addEventListener('pointerdown', () => { c.dataset.touched = '1'; });
    }
    if (fine && !c.closest('[data-drag-only]')) {
      c.addEventListener('mousemove', e => {
        if (e.buttons) return;
        c.dataset.touched = '1';
        const r = c.getBoundingClientRect();
        setCompare(c, gsap_clamp((e.clientX - r.left) / r.width * 100));
      });
    }
  });
  function gsap_clamp(v) { return Math.max(0, Math.min(100, v)); }

  /* Image following the pointer over a list */
  const float = $('.float-img');
  if (float && fine) {
    const imgs = $$('img', float);
    const qx = motion ? gsap.quickTo(float, 'x', { duration: .55, ease: 'power3' }) : null;
    const qy = motion ? gsap.quickTo(float, 'y', { duration: .55, ease: 'power3' }) : null;
    $$('[data-float]').forEach(row => {
      row.addEventListener('mouseenter', () => {
        imgs.forEach(i => i.classList.toggle('on', i.dataset.key === row.dataset.float));
        float.style.opacity = 1; float.style.scale = '1.16';
      });
      row.addEventListener('mouseleave', () => { float.style.opacity = 0; float.style.scale = '1'; });
      row.addEventListener('mousemove', e => {
        const x = Math.min(e.clientX + 24, innerWidth - float.offsetWidth * 1.1), y = e.clientY - float.offsetHeight * .55;
        if (qx) { qx(x); qy(y); } else { float.style.transform = `translate(${x}px,${y}px)`; }
      });
    });
  }

  /* Custom cursor label */
  const cursor = $('.cursor');
  if (cursor && fine && motion) {
    const qx = gsap.quickTo(cursor, 'x', { duration: .35, ease: 'power3' });
    const qy = gsap.quickTo(cursor, 'y', { duration: .35, ease: 'power3' });
    addEventListener('mousemove', e => { qx(e.clientX); qy(e.clientY); });
    const bind = () => $$('[data-cursor]').forEach(el => {
      if (el.dataset.cb) return; el.dataset.cb = '1';
      el.addEventListener('mouseenter', () => { cursor.textContent = el.dataset.cursor; gsap.to(cursor, { scale: 1, opacity: 1, duration: .45, ease: 'expo.out' }); });
      el.addEventListener('mouseleave', () => gsap.to(cursor, { scale: 0, opacity: 0, duration: .3 }));
    });
    bind();
    window.MMA_BIND_CURSOR = bind;
  }

  /* Magnetic buttons */
  if (fine && motion) $$('.btn').forEach(b => {
    b.addEventListener('mousemove', e => {
      const r = b.getBoundingClientRect();
      gsap.to(b, { x: (e.clientX - r.left - r.width / 2) * .16, y: (e.clientY - r.top - r.height / 2) * .24, duration: .5, ease: 'power3.out' });
    });
    b.addEventListener('mouseleave', () => gsap.to(b, { x: 0, y: 0, duration: .8, ease: 'elastic.out(1,.45)' }));
  });

  /* Project filters and view toggle */
  const pi = $('.pi-grid');
  if (pi) {
    const chips = $$('[data-filter]'), items = $$('[data-type]');
    chips.forEach(ch => ch.addEventListener('click', () => {
      const f = ch.dataset.filter;
      chips.forEach(c => c.setAttribute('aria-pressed', c === ch));
      items.forEach(it => it.classList.toggle('hide', f !== 'all' && it.dataset.type !== f));
      pi.classList.toggle('filtered', f !== 'all');
      if (motion) {
        gsap.fromTo($$('.pcard:not(.hide)', pi), { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: .8, stagger: .06, ease: 'expo.out' });
        ScrollTrigger.refresh();
      }
    }));
    $$('[data-view]').forEach(v => v.addEventListener('click', () => {
      $$('[data-view]').forEach(x => x.setAttribute('aria-pressed', x === v));
      root.classList.toggle('list-view', v.dataset.view === 'list');
      if (motion) ScrollTrigger.refresh();
    }));
  }

  /* Plan magnifier */
  $$('.plan-wrap').forEach(w => {
    const lens = $('.lens', w), img = $('img', w);
    if (!lens || !fine) return;
    const Z = 2.6;
    w.addEventListener('mouseenter', () => { lens.style.opacity = 1; lens.style.backgroundImage = `url(${img.currentSrc || img.src})`; });
    w.addEventListener('mouseleave', () => { lens.style.opacity = 0; });
    w.addEventListener('mousemove', e => {
      const r = img.getBoundingClientRect(), wr = w.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      lens.style.left = (e.clientX - wr.left) + 'px'; lens.style.top = (e.clientY - wr.top) + 'px';
      lens.style.backgroundSize = `${r.width * Z}px ${r.height * Z}px`;
      lens.style.backgroundPosition = `${120 - x * Z}px ${120 - y * Z}px`;
    });
  });

  /* Project brief wizard */
  const brief = $('#brief');
  if (brief) initBrief(brief);

  function initBrief(form) {
    const I = window.MMA_I18N, steps = $$('.step', form), bar = $('.brief-bar i');
    const sides = $$('.brief-side img');
    const state = { type: null, stage: null, budget: null };
    const params = new URLSearchParams(location.search);
    if (params.get('type')) state.type = params.get('type');
    if (params.get('stage')) state.stage = params.get('stage');
    const study = params.get('study');
    let at = 0;
    const lang = root.lang;

    const show = n => {
      at = n;
      steps.forEach((s, i) => s.classList.toggle('on', i === n));
      bar.style.width = ((n + 1) / steps.length * 100) + '%';
      $('.brief-err').textContent = '';
      $('#briefBack').style.visibility = n === 0 ? 'hidden' : 'visible';
      $('#briefNext').parentElement.style.display = n === steps.length - 1 ? 'none' : '';
      const key = state.type || 'default';
      sides.forEach(im => im.classList.toggle('on', im.dataset.key === key));
      if (n === steps.length - 1) buildSummary();
    };
    const sync = () => {
      $$('[data-field]', form).forEach(b => b.setAttribute('aria-pressed', state[b.dataset.field] === b.dataset.value));
      const key = state.type || 'default';
      sides.forEach(im => im.classList.toggle('on', im.dataset.key === key));
    };
    $$('[data-field]', form).forEach(b => b.addEventListener('click', () => {
      state[b.dataset.field] = b.dataset.value;
      sync();
      setTimeout(() => { if (at < steps.length - 2) show(at + 1); }, 240);
    }));
    const valid = () => {
      if (at === 0 && !state.type) return I.errType;
      if (at === 1 && !state.stage) return I.errStage;
      if (at === steps.length - 2) {
        if (!$('#fName').value.trim() || !$('#fPhone').value.trim()) return I.errContact;
      }
      return '';
    };
    $('#briefNext').addEventListener('click', () => {
      const err = valid();
      if (err) { $('.brief-err').textContent = err; return; }
      show(Math.min(at + 1, steps.length - 1));
    });
    $('#briefBack').addEventListener('click', () => show(Math.max(0, at - 1)));

    function labelOf(field) {
      const b = $(`[data-field="${field}"][data-value="${state[field]}"] strong`, form);
      return b ? b.textContent : '';
    }
    function buildSummary() {
      const rows = [
        [I.sType, labelOf('type')],
        [I.sStage, labelOf('stage')],
        [I.sCity, $('#fCity').value.trim()],
        [I.sBudget, labelOf('budget')],
        [I.sStudy, study || ''],
        [I.sName, $('#fName').value.trim()],
        [I.sPhone, $('#fPhone').value.trim()],
        [I.sMsg, $('#fMsg').value.trim()]
      ].filter(r => r[1]);
      const box = $('#summary');
      box.textContent = '';
      rows.forEach(([k, v]) => {
        const d = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
        dt.textContent = k; dd.textContent = v; d.append(dt, dd); box.append(d);
      });
      const m = I.matches[state.type];
      const match = $('#match');
      if (m) {
        $('img', match).src = m.img;
        $('strong', match).textContent = m.name;
        match.href = m.url;
        match.classList.remove('hide');
      } else match.classList.add('hide');
      const text = [I.waIntro].concat(rows.map(([k, v]) => `${k}: ${v}`)).join('\n');
      $$('[data-wa]').forEach(a => { a.href = `https://wa.me/${a.dataset.wa}?text=${encodeURIComponent(text)}`; });
    }
    sync();
    show(params.get('type') ? (params.get('stage') ? 2 : 1) : 0);
    form.addEventListener('submit', e => e.preventDefault());
  }

  /* Live 3D teaser loads only when near the viewport */
  const teaser = $('[data-lab-teaser]');
  if (teaser) {
    const io = new IntersectionObserver(es => {
      if (!es.some(e => e.isIntersecting)) return;
      io.disconnect();
      import(new URL(teaser.dataset.module, location.href).href).then(m => m.mountTeaser(teaser)).catch(() => {
        teaser.style.background = `url(${teaser.dataset.fallback}) center/cover`;
      });
    }, { rootMargin: '400px' });
    io.observe(teaser);
  }
})();
