/* Public observations are a separate, human-reviewed projection, never case states. */
(() => {
  const host = document.querySelector('[data-observation-bulletin]');
  if (!host) return;
  fetch('/observations/feed.json', {cache: 'no-cache'}).then(r => {
    if (!r.ok) throw new Error('Feed unavailable');
    return r.json();
  }).then(feed => {
    const items = feed.items.filter(x => x.publication_status === 'APPROVED' &&
      /^\d{4}-\d{2}-\d{2}$/.test(x.observed_on) &&
      typeof x.summary === 'string' && typeof x.boundary === 'string' &&
      typeof x.case_url === 'string' && (x.case_url.startsWith('/cases/') ||
        x.case_url.startsWith('https://github.com/roalstoney-alt/se-dual-case-public/')));
    if (!items.length) return;
    host.hidden = false;
    const list = host.querySelector('ol');
    items.forEach(x => {
      const li = document.createElement('li');
      const label = document.createElement('p');
      label.textContent = `${x.observed_on} · ${x.case_id} · ${x.type}`;
      const summary = document.createElement('p'); summary.textContent = x.summary;
      const boundary = document.createElement('p'); boundary.textContent = `Boundary: ${x.boundary}`;
      const link = document.createElement('a'); link.href = x.case_url;
      link.textContent = 'Review this case and challenge its boundary';
      li.append(label, summary, boundary, link); list.append(li);
    });
    const cards = [...list.children]; let index = 0, paused = false, timer;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const button = host.querySelector('button');
    const previous = document.createElement('button'); previous.type = 'button'; previous.textContent = 'Previous observation';
    const next = document.createElement('button'); next.type = 'button'; next.textContent = 'Next observation';
    button.after(previous, next);
    const show = () => cards.forEach((card, i) => { card.hidden = i !== index; });
    const stop = () => { clearInterval(timer); timer = undefined; };
    const start = () => {
      stop();
      if (!paused && !reduced.matches && !document.hidden && !host.matches(':hover') &&
          !host.contains(document.activeElement) && cards.length > 1)
        timer = setInterval(() => { index = (index + 1) % cards.length; show(); }, 12000);
    };
    button.hidden = cards.length < 2;
    previous.hidden = next.hidden = cards.length < 2;
    previous.addEventListener('click', () => { index = (index + cards.length - 1) % cards.length; show(); });
    next.addEventListener('click', () => { index = (index + 1) % cards.length; show(); });
    button.addEventListener('click', () => {
      paused = !paused; button.textContent = paused ? 'Resume rotation' : 'Pause rotation';
      button.setAttribute('aria-pressed', String(paused)); start();
    });
    host.addEventListener('mouseenter', stop);
    host.addEventListener('mouseleave', start);
    host.addEventListener('focusin', stop);
    host.addEventListener('focusout', e => { if (!host.contains(e.relatedTarget)) start(); });
    reduced.addEventListener('change', start);
    document.addEventListener('visibilitychange', start);
    show(); start();
  }).catch(() => { /* Static history link remains available; no invented observation. */ });
})();
