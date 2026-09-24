import {initFrontier} from './frontier.mjs';
import {calculate, searchLibrary} from './calculations.mjs';

const {client: config, labels, tools} = JSON.parse(document.querySelector('#frontend-config').textContent);
const one = (selector, root = document) => root.querySelector(selector);
const all = (selector, root = document) => [...root.querySelectorAll(selector)];
const toastElement = one('.toast');
let toastTimer;
function toast(message) {
  toastElement.textContent = message;
  toastElement.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastElement.classList.remove('visible'), config.toast_duration);
}

let saved = new Set();
function loadSaved() {
  try {
    const value = JSON.parse(localStorage.getItem(config.reading_storage_key) || '[]');
    saved = new Set(Array.isArray(value) ? value.filter(Number.isSafeInteger).slice(0, config.max_saved) : []);
  } catch { saved = new Set(); }
}
function persist(next) {
  try { localStorage.setItem(config.reading_storage_key, JSON.stringify([...next])); saved = next; return true; }
  catch { toast(labels.storage_error); return false; }
}
function updateSaved() {
  all('[data-save]').forEach(button => {
    const active = saved.has(Number(button.dataset.save));
    button.setAttribute('aria-pressed', String(active));
    button.setAttribute('aria-label', active ? labels.unsave : labels.save);
    const label = one('[data-save-label]', button);
    if (label) label.textContent = active ? labels.unsave : labels.save;
  });
  all('[data-saved-count]').forEach(count => { count.textContent = saved.size; count.hidden = !saved.size; });
  filterArchive();
}
loadSaved();
all('[data-save]').forEach(button => button.addEventListener('click', () => {
  const id = Number(button.dataset.save);
  const next = new Set(saved);
  if (next.has(id)) next.delete(id);
  else if (next.size < config.max_saved) next.add(id);
  else { toast(labels.list_full); return; }
  if (persist(next)) { updateSaved(); toast(next.has(id) ? labels.saved : labels.removed); }
}));
one('[data-clear-saved]')?.addEventListener('click', () => {
  if (persist(new Set())) { updateSaved(); toast(labels.list_cleared); }
});
window.addEventListener('storage', event => {
  if (event.key === config.reading_storage_key || event.key === null) { loadSaved(); updateSaved(); }
});

function filterArchive() {
  const archive = one('[data-archive]');
  if (!archive) return;
  const query = one('[data-filter-search]', archive).value.trim().toLocaleLowerCase();
  const category = one('[data-filter-category]', archive).value;
  let count = 0;
  all('[data-card]', archive).forEach(card => {
    const visible = (!archive.hasAttribute('data-reading-list') || saved.has(Number(card.dataset.id))) &&
      (!category || card.dataset.category === category) && card.dataset.search.includes(query);
    card.hidden = !visible;
    if (visible) count++;
  });
  one('[data-result-count]', archive).textContent = count;
  one('.empty-state', archive).hidden = count !== 0;
}
all('[data-filter-search]').forEach(input => input.addEventListener('input', filterArchive));
all('[data-filter-category]').forEach(input => input.addEventListener('change', filterArchive));
updateSaved();

const menu = one('.menu-toggle');
function closeMenu() {
  if (one('.main-nav').contains(document.activeElement)) menu.focus();
  menu.setAttribute('aria-expanded', 'false'); one('.main-nav').classList.remove('open');
}
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  one('.main-nav').classList.toggle('open', open);
});
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });
const dialogOpeners = new WeakMap();
all('[data-open]').forEach(button => button.addEventListener('click', () => {
  closeMenu();
  const dialog = document.getElementById(button.dataset.open);
  dialogOpeners.set(dialog, button);
  dialog.showModal();
  one('input', dialog).focus();
}));
all('dialog').forEach(dialog => {
  dialog.addEventListener('close', () => dialogOpeners.get(dialog)?.focus());
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); dialog.close(); }
  });
  one('[data-close]', dialog).addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    }
  });
});

let libraryPromise;
async function library() {
  if (!libraryPromise) libraryPromise = fetch(config.search_index).then(response => {
    if (!response.ok) throw new Error('Library unavailable');
    return response.json();
  }).catch(error => { libraryPromise = null; throw error; });
  return libraryPromise;
}
all('[data-library-search]').forEach(input => input.addEventListener('input', async () => {
  const query = input.value.trim();
  const results = one('.search-results', input.closest('dialog'));
  results.replaceChildren();
  const note = message => { const p = document.createElement('p'); p.className = 'muted'; p.textContent = message; results.append(p); };
  if (!query) { note(labels.assistant_intro); return; }
  try {
    const items = await library();
    if (query !== input.value.trim()) return;
    results.replaceChildren();
    const matches = searchLibrary(items, query, config.search_limit);
    if (!matches.length) note(labels.search_empty);
    for (const item of matches) {
      if (!item.route.startsWith('/') || item.route.startsWith('//')) continue;
      const link = document.createElement('a'); link.href = item.route;
      const category = document.createElement('small'); category.textContent = `${item.category} · ${item.minutes} min read`;
      const title = document.createElement('strong'); title.textContent = item.title;
      link.append(category, title); results.append(link);
    }
  } catch { if (query === input.value.trim()) { results.replaceChildren(); note(labels.assistant_error); } }
}));

all('[data-tool]').forEach(form => {
  let imageUrl;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const kind = form.dataset.tool;
    const definition = tools[kind];
    const output = one('.tool-output', form);
    const button = one('[type=submit]', form);
    output.replaceChildren(); output.hidden = false;
    button.disabled = true;
    try {
      const values = Object.fromEntries(new FormData(form));
      if (definition.kind === 'image') {
        const file = values.image;
        if (!definition.accept.split(',').includes(file.type) || file.size > config.max_image_bytes) throw new Error(labels.image_size_error);
        const bitmap = await createImageBitmap(file);
        if (bitmap.width * bitmap.height > config.max_image_pixels) { bitmap.close(); throw new Error(labels.image_size_error); }
        const canvas = document.createElement('canvas');
        const ratio = Math.min(1, config.image_max_width / bitmap.width);
        canvas.width = Math.max(1, Math.round(bitmap.width * ratio));
        canvas.height = Math.max(1, Math.round(bitmap.height * ratio));
        canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height); bitmap.close();
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/webp', config.image_quality));
        if (!blob || blob.type !== 'image/webp') throw new Error(labels.image_format_error);
        if (imageUrl) URL.revokeObjectURL(imageUrl);
        imageUrl = URL.createObjectURL(blob);
        const text = document.createElement('p'); text.textContent = `${canvas.width} × ${canvas.height} px · ${(blob.size / 1024).toFixed(1)} KB`;
        const link = document.createElement('a'); link.href = imageUrl; link.download = definition.download; link.textContent = labels.image_download;
        output.append(text, link);
      } else {
        const result = calculate(kind, values, definition, tools._messages);
        if (typeof result === 'number') {
          const value = document.createElement('strong'); value.textContent = result.toFixed(1);
          const label = document.createElement('span'); label.textContent = definition.result_label;
          output.append(value, label);
        } else if (kind === 'scores') {
          output.textContent = definition.groups.map(group => `${group.name}: ${result[group.id]}`).join('\n');
        } else {
          const text = document.createElement('p'); text.textContent = result;
          const copy = document.createElement('button'); copy.type = 'button'; copy.className = 'text-link'; copy.textContent = labels.copy;
          copy.addEventListener('click', async () => {
            try { await navigator.clipboard.writeText(result); toast(labels.copied); } catch { toast(labels.copy_error); }
          }); output.append(text, copy);
        }
      }
    } catch (error) { output.textContent = error instanceof Error ? error.message : labels.tool_error; }
    finally { button.disabled = false; }
  });
  window.addEventListener('pagehide', () => { if (imageUrl) URL.revokeObjectURL(imageUrl); });
});

const motion = matchMedia('(prefers-reduced-motion: reduce)');
const finePointer = matchMedia('(pointer: fine)');
const art = one('.hero-art');
art?.addEventListener('pointermove', event => {
  if (motion.matches || !finePointer.matches) return;
  const rect = art.getBoundingClientRect();
  art.style.setProperty('--tilt-x', `${((event.clientX - rect.left) / rect.width - .5) * config.motion_max_tilt}deg`);
  art.style.setProperty('--tilt-y', `${-((event.clientY - rect.top) / rect.height - .5) * config.motion_max_tilt}deg`);
});
function resetArt() { art?.style.removeProperty('--tilt-x'); art?.style.removeProperty('--tilt-y'); }
art?.addEventListener('pointerleave', resetArt);
motion.addEventListener('change', resetArt);
let scrollScheduled = false;
window.addEventListener('scroll', () => {
  if (scrollScheduled || motion.matches) return;
  scrollScheduled = true;
  requestAnimationFrame(() => {
    const extent = document.documentElement.scrollHeight - innerHeight;
    one('.reading-progress').style.transform = `scaleX(${extent > 0 ? Math.min(1, scrollY / extent) : 0})`;
    scrollScheduled = false;
  });
}, {passive: true});

initFrontier(config.frontier);
