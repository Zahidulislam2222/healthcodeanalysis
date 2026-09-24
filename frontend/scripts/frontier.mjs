/** One owner for the bounded film sequence; native page scrolling remains intact. */
export function initFrontier(settings) {
  const section = document.querySelector('[data-frontier-sequence]');
  if (!section) return;
  const stage = section.querySelector('[data-frontier]');
  const video = section.querySelector('video');
  const toggle = section.querySelector('[data-motion-toggle]');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const wide = matchMedia(`(min-width: ${settings.minimum_width}px) and (min-height: ${settings.minimum_height + 1}px)`);
  let ready = false;
  let paused = false;
  let desired = 0;
  let scheduled = false;
  let failed = false;
  const clamp = value => Math.max(0, Math.min(1, value));
  const active = () => ready && wide.matches && !reduced.matches && !failed;
  function seek() {
    if (!active() || paused || video.seeking || document.hidden) return;
    if (Math.abs(video.currentTime - desired) > settings.seek_epsilon) video.currentTime = desired;
  }
  function update() {
    scheduled = false;
    if (!active() || paused) return;
    const rect = section.getBoundingClientRect();
    const extent = section.offsetHeight - innerHeight;
    const progress = extent > 0 ? clamp(-rect.top / extent) : 0;
    desired = progress * Math.max(0, video.duration - settings.end_padding);
    seek();
    const fade = clamp((progress - settings.headline_fade_start) / (settings.headline_fade_end - settings.headline_fade_start));
    const caption = clamp((progress - settings.caption_start) / (settings.caption_end - settings.caption_start));
    stage.style.setProperty('--intro-opacity', String(1 - fade));
    stage.style.setProperty('--intro-y', `${-fade * 35}px`);
    stage.style.setProperty('--caption-opacity', String(caption));
    section.dataset.progress = progress.toFixed(3);
  }
  function schedule() { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } }
  function configure() {
    const enabled = wide.matches && !reduced.matches && !failed;
    if (enabled && !video.hasAttribute('src')) { video.src = settings.video_url; video.load(); }
    section.classList.toggle('has-cinema', enabled && ready);
    toggle.hidden = !enabled || !ready;
    video.hidden = !enabled || !ready;
    if (!enabled) {
      stage.style.removeProperty('--intro-opacity');
      stage.style.removeProperty('--intro-y');
      stage.style.removeProperty('--caption-opacity');
      section.dataset.progress = '0';
    }
    schedule();
  }
  video.addEventListener('loadeddata', () => { ready = Number.isFinite(video.duration); configure(); });
  video.addEventListener('error', () => { failed = true; configure(); });
  video.addEventListener('seeked', seek);
  toggle.addEventListener('click', () => {
    paused = !paused;
    toggle.textContent = paused ? settings.resume_label : settings.pause_label;
    toggle.setAttribute('aria-pressed', String(paused));
    if (!paused) schedule();
  });
  toggle.textContent = settings.pause_label;
  toggle.setAttribute('aria-pressed', 'false');
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  window.addEventListener('pageshow', schedule);
  document.addEventListener('visibilitychange', schedule);
  reduced.addEventListener('change', configure);
  wide.addEventListener('change', configure);
  configure();
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.unobserve(entry.target);
        if (!reduced.matches) entry.target.animate([
          {opacity:.5, transform:`translateY(${settings.reveal_distance}px)`},
          {opacity:1, transform:'translateY(0)'}
        ], {duration:settings.reveal_duration, easing:'cubic-bezier(.22,.61,.36,1)'});
      }
    }, {threshold:.15});
    document.querySelectorAll('.path-item,.frontier-lead,.frontier-tool,.frontier-manifesto h2').forEach(el => observer.observe(el));
    reduced.addEventListener('change', () => {
      if (reduced.matches) document.getAnimations().forEach(animation => animation.finish());
    });
    window.addEventListener('pagehide', () => observer.disconnect(), {once:true});
  }
}
