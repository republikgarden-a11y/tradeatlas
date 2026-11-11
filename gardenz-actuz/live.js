'use strict';
(() => {
  const el = id => document.getElementById(id);
  const store = { get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }, set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch {} } };
  const normalize = text => String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const dayLabel = value => new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(value.length === 10 ? value + 'T12:00:00Z' : value));
  const timeLabel = value => new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' }).format(new Date(value));
  const languageLabel = code => ({ fr: 'Français', en: 'Anglais', de: 'Allemand' }[code] || code);
  const node = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const safeURL = value => { try { const u = new URL(value, location.href); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch { return ''; } };
  const bookmarkIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"/></svg>';
  let news = null, archive = null, editionsIndex = [], active = 'live', topic = '', busy = false, limit = 12, offline = false, archiveRequest = 0;
  let saved = new Set(store.get('actuz-saved', [])), savedItems = store.get('actuz-saved-items', {});
  const initial = new URL(location.href);
  const translator = window.GardenzTranslation;
  let french = store.get('actuz-french', true) !== false;
  function sourceLink(item, text, original = false) {
    const a = node('a', text); a.href = translator.readerURL(item, french, original); a.target = '_blank'; a.rel = 'noopener noreferrer';
    a.hreflang = french && item.language !== 'fr' && !original ? 'fr' : item.language || '';
    if (french && item.language !== 'fr' && !original) a.title = 'Lire l’article complet en français avec Google Traduction · nouvel onglet';
    return a;
  }
  function syncTranslation() {
    el('translation-toggle').setAttribute('aria-checked', String(french));
    el('translation-toggle-label').textContent = french ? 'Français : activé' : 'Français : désactivé';
    if (active === 'archives') { el('translation-status').textContent = 'Ces anciennes éditions sont déjà rédigées en français.'; return; }
    if (!french) { el('translation-status').textContent = 'Les textes d’origine sont affichés. Réactive le français à tout moment.'; return; }
    const foreign = viewCorpus().filter(item => item.language !== 'fr');
    const translated = foreign.filter(translator.valid).length;
    el('translation-status').textContent = foreign.length && translated < foreign.length
      ? translated + '/' + foreign.length + ' articles étrangers traduits. « Lire en français » reste disponible pour les autres.'
      : 'Titres et extraits en français · traduction automatique · original disponible en un clic.';
  }
  function saveButton(item) {
    const button = node('button', undefined, 'save-news'); button.type = 'button'; button.innerHTML = bookmarkIcon;
    const selected = saved.has(item.id); button.dataset.itemId = item.id; button.append(node('span', selected ? 'Gardé' : 'Garder'));
    button.setAttribute('aria-label', (selected ? 'Retirer de mes articles : ' : 'Garder pour plus tard : ') + translator.display(item, french).title);
    button.setAttribute('aria-pressed', String(selected));
    button.addEventListener('click', () => {
      if (saved.has(item.id)) { saved.delete(item.id); delete savedItems[item.id]; } else { saved.add(item.id); savedItems[item.id] = item; }
      store.set('actuz-saved', [...saved]); store.set('actuz-saved-items', savedItems);
      const oldFocus = document.activeElement; render();
      const replacement = [...document.querySelectorAll('.save-news')].find(b => b.dataset.itemId === item.id);
      if (oldFocus === button) replacement?.focus({ preventScroll: true });
    }); return button;
  }
  function article(item, lead = false) {
    const text = translator.display(item, french);
    const wrapper = node('article', undefined, (lead ? 'lead-story' : 'news-item') + (!item.image ? ' no-image' : '')); wrapper.id = 'news-' + item.id;
    if (item.image && /^assets\/[\w-]+\.(jpg|jpeg|png|webp)$/.test(item.image)) {
      const figure = node('figure', undefined, 'news-image'), link = sourceLink(item);
      const img = node('img'); img.src = item.image; img.alt = 'Visuel de l’article publié par ' + item.source; img.decoding = 'async'; img.loading = lead ? 'eager' : 'lazy';
      if (lead) img.fetchPriority = 'high'; img.width = 800; img.height = 480;
      img.addEventListener('error', () => { figure.remove(); wrapper.classList.add('no-image'); }, { once: true }); link.append(img); figure.append(link);
      figure.append(node('figcaption', item.source + ' · image de l’article')); wrapper.append(figure);
    }
    const copy = node('div', undefined, 'news-copy'), meta = node('p', undefined, 'news-meta');
    meta.append(node('span', item.source, 'source-name'), node('span', timeLabel(item.publishedAt)), node('span', text.translated ? 'Français · traduit de ' + ({en:'l’anglais',de:'l’allemand'}[item.language] || languageLabel(item.language)) : text.unavailable ? 'Source en ' + languageLabel(item.language).toLowerCase() : languageLabel(item.language), text.translated ? 'translated-label' : ''));
    copy.append(meta);
    if (item.kind && item.kind !== 'Article') copy.append(node('p', item.kind, 'article-kind'));
    const h = node(lead ? 'h2' : 'h3'); h.lang = text.language || 'fr'; h.append(sourceLink(item, text.title)); copy.append(h);
    if (text.excerpt) { const excerpt = node('p', text.excerpt, text.unavailable ? 'translation-unavailable' : 'news-excerpt'); excerpt.lang = text.unavailable ? 'fr' : text.language || 'fr'; copy.append(excerpt); }
    const tail = node('div', undefined, 'news-tail'), links = node('div', undefined, 'source-links');
    const link = sourceLink(item, french && item.language !== 'fr' ? 'Lire en français' : 'Lire l’article'); link.className = 'read-source';
    links.append(link);
    if (french && item.language !== 'fr') { const original = sourceLink(item, 'Source originale', true); original.className = 'original-source'; links.append(original); }
    tail.append(links, saveButton(item)); copy.append(tail); wrapper.append(copy); return wrapper;
  }
  function currentData() { return active === 'daily' ? archive : news; }
  function viewCorpus() {
    if (active !== 'saved') return [...(currentData()?.items || [])];
    return translator.savedCorpus(news?.items || [], savedItems, saved);
  }
  function itemsForView() {
    const items = viewCorpus();
    const query = normalize(el('live-query').value).split(/\s+/).filter(Boolean), lang = el('live-language').value, source = el('live-source').value;
    const since = Date.now() - Number(el('live-period').value) * 3600000;
    return items.filter(i => (active !== 'live' || new Date(i.publishedAt).getTime() >= since) && (!topic || i.topics?.includes(topic)) && (!lang || i.language === lang) && (!source || i.source === source) && query.every(q => normalize(i.title + ' ' + i.excerpt + ' ' + (translator.valid(i) ? i.translation.title + ' ' + i.translation.excerpt : '') + ' ' + i.source + ' ' + (i.topics || []).join(' ')).includes(q)))
      .sort((a, b) => (a.language !== 'fr') - (b.language !== 'fr') || new Date(b.publishedAt) - new Date(a.publishedAt));
  }
  function renderHealth() {
    if (!news) return;
    const age = news.lastSuccess ? (Date.now() - new Date(news.lastSuccess)) / 3600000 : Infinity;
    el('news-status').textContent = offline ? 'Hors connexion · journal conservé' : news.status === 'error' ? 'Collecte interrompue · articles conservés' : age > 30 ? 'La mise à jour a du retard' : news.status === 'partial' ? 'Journal actualisé · certaines sources indisponibles' : 'Ton journal est à jour';
    el('news-status').dataset.state = offline || news.status === 'error' || age > 30 ? 'warning' : 'ok';
    const healthy = news.sources.filter(s => s.ok).length;
    el('news-checked').textContent = (news.lastSuccess ? 'Collecté le ' + timeLabel(news.lastSuccess) + ' · Paris' : 'Aucune collecte réussie') + ' · ' + healthy + '/' + news.sources.length + ' sources accessibles';
    el('refresh-note').textContent = 'Collectes prévues chaque jour à ' + (news.schedule || '09h17, 13h17 et 18h17 · Paris') + '. Le bouton recharge le dernier journal publié.';
    el('today-label').textContent = dayLabel(new Date().toISOString());
    const list = el('sources-health'); list.replaceChildren();
    for (const source of news.sources) {
      const li = node('li'), name = node('a', source.name); name.href = safeURL(source.url); name.target = '_blank'; name.rel = 'noopener noreferrer';
      li.append(name, node('span', source.ok ? 'Accessible' : 'Indisponible · ' + (source.error || 'réessaie à la prochaine collecte'), source.ok ? 'source-ok' : 'source-unavailable')); list.append(li);
    }
  }
  function renderFrontpage() {
    const fresh = (news?.items || []).filter(i => Date.now() - new Date(i.publishedAt) <= 86400000)
      .sort((a, b) => (a.language !== 'fr') - (b.language !== 'fr') || new Date(b.publishedAt) - new Date(a.publishedAt));
    el('frontpage').hidden = active !== 'live' || !fresh.length;
    if (!fresh.length) return;
    el('lead-story').replaceChildren(article(fresh[0], true));
    const list = el('briefing-list'); list.replaceChildren();
    for (const item of fresh.slice(1, 5)) {
      const li = node('li'); li.append(node('span', item.topics?.[0] || item.source, 'briefing-topic'));
      const text = translator.display(item, french), link = sourceLink(item, text.title); link.lang = text.language; li.append(link, node('small', item.source + ' · ' + (text.translated ? 'Traduit en français' : text.unavailable ? 'Traduction disponible à l’ouverture' : languageLabel(item.language)))); list.append(li);
    }
    if (!list.children.length) list.append(node('li', 'Une journée calme : les titres disponibles sont dans le fil ci-dessous.'));
  }
  function render() {
    syncTranslation();
    if (!news) return;
    renderHealth(); renderFrontpage();
    el('saved-count').textContent = saved.size;
    el('live-period').disabled = active !== 'live';
    el('all-news-title').textContent = active === 'daily' ? 'Revue de presse du ' + (archive?.date ? dayLabel(archive.date) : 'jour sélectionné') : active === 'saved' ? 'Tes articles à retrouver' : 'Le fil de l’actualité';
    const items = itemsForView();
    el('live-count').textContent = items.length + ' article' + (items.length !== 1 ? 's' : '');
    el('filter-context').textContent = active === 'saved' ? 'Ta sélection, conservée sur cet appareil.' : active === 'daily' ? 'Publications rassemblées dans cette édition. Les dates des articles restent celles des sources.' : 'Sources francophones en premier, puis publications les plus récentes. Recherche sur les 30 derniers jours avec le filtre Période.';
    const list = el('news-list'); list.replaceChildren();
    if (!items.length) {
      const empty = node('div', undefined, 'empty-news');
      empty.append(node('h3', active === 'saved' && !saved.size ? 'Ton coin lecture attend ses premières trouvailles.' : 'Aucun article avec ces filtres.'));
      empty.append(node('p', active === 'saved' && !saved.size ? 'Appuie sur « Garder » sous un article pour le retrouver ici.' : 'Essaie une autre rubrique, une période plus large ou efface tes filtres.'));
      list.append(empty);
    } else for (const item of items.slice(0, limit)) list.append(article(item));
    el('load-more').hidden = items.length <= limit; el('load-more').textContent = 'Afficher les articles suivants (' + Math.max(0, items.length - limit) + ')';
    document.querySelectorAll('[data-topic]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.topic === topic)));
  }
  function resetFilters() { topic = ''; el('live-query').value = ''; el('live-language').value = ''; el('live-source').value = ''; el('live-period').value = '24'; limit = 12; render(); }
  function setView(view, push = true) {
    active = view; el('live-panel').hidden = view === 'archives'; el('archive-panel').hidden = view !== 'archives'; el('daily-controls').hidden = view !== 'daily';
    document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
    document.title = 'Gardenz Actuz — ' + ({ live: 'Dernières actus', daily: 'Éditions quotidiennes', saved: 'Mes articles', archives: 'Anciennes éditions' }[view]);
    if (push) { const url = new URL(location.href); url.search = ''; url.hash = ''; if (view !== 'live') url.searchParams.set('view', view); if (view === 'daily' && el('daily-edition').value) url.searchParams.set('edition', el('daily-edition').value); history.pushState({}, '', url); }
    resetFilters();
    if (view === 'daily' && editionsIndex.length && !archive) loadEdition(el('daily-edition').value || editionsIndex[0].date);
  }
  function validData(value) { return value && Array.isArray(value.items) && Array.isArray(value.sources) && value.items.every(i => i && typeof i.id === 'string' && typeof i.title === 'string' && !!safeURL(i.url) && Number.isFinite(Date.parse(i.publishedAt))); }
  async function getJSON(path) {
    const response = await fetch(path + '?v=' + Date.now(), { cache: 'no-store', signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error('HTTP ' + response.status); return { data: await response.json(), offline: response.headers.get('X-Gardenz-Cache') === 'offline' };
  }
  async function loadEdition(day) {
    const entry = editionsIndex.find(item => item.date === day); if (!entry || !/^data\/history\/\d{4}-\d{2}-\d{2}\.json$/.test(entry.path)) return;
    const request = ++archiveRequest; el('daily-description').textContent = 'Chargement de l’édition…';
    try {
      const { data } = await getJSON(entry.path); if (!validData(data)) throw new Error('Édition invalide'); if (request !== archiveRequest) return;
      archive = { ...data, date: day }; el('daily-description').textContent = data.items.length + ' articles · collecte du ' + timeLabel(data.lastSuccess) + ' · Paris'; limit = 12; render();
    } catch { if (request !== archiveRequest) return; archive = { date: day, items: [] }; el('daily-description').textContent = 'Cette édition n’a pas pu se charger. Vérifie ta connexion, puis sélectionne à nouveau sa date.'; render(); }
  }
  async function refresh() {
    if (busy) return; busy = true; el('refresh-news').disabled = true;
    try {
      const response = await getJSON('data/latest.json'); if (!validData(response.data)) throw new Error('Format invalide'); news = response.data; offline = response.offline; store.set('actuz-news-cache', news);
      for (const item of news.items) if (saved.has(item.id)) savedItems[item.id] = item;
      store.set('actuz-saved-items', savedItems);
      const selected = el('live-source').value; el('live-source').replaceChildren(node('option', 'Tous les médias')); el('live-source').firstChild.value = '';
      [...new Set([...news.sources.map(i => i.name), ...Object.values(savedItems).map(i => i.source)])].sort().forEach(name => { const option = node('option', name); option.value = name; el('live-source').append(option); }); el('live-source').value = selected;
      render();
      try {
        const index = await getJSON('data/index.json');
        if (Array.isArray(index.data.editions)) { editionsIndex = index.data.editions; store.set('actuz-editions-index', editionsIndex); }
      } catch { editionsIndex = store.get('actuz-editions-index', []); }
      const previous = el('daily-edition').value || initial.searchParams.get('edition'); el('daily-edition').replaceChildren();
      for (const entry of editionsIndex) { const option = node('option', dayLabel(entry.date) + ' · ' + entry.count + ' articles'); option.value = entry.date; el('daily-edition').append(option); }
      if (editionsIndex.some(e => e.date === previous)) el('daily-edition').value = previous;
      if (!editionsIndex.length) { el('daily-edition').append(node('option', 'Aucune édition quotidienne disponible')); el('daily-description').textContent = 'Les éditions apparaissent ici après leur première collecte.'; }
      if (active === 'daily' && el('daily-edition').value) await loadEdition(el('daily-edition').value);
    } catch {
      news ||= store.get('actuz-news-cache', null); offline = true;
      if (news) render(); else { el('news-status').textContent = 'Le journal n’a pas pu se charger'; el('news-checked').textContent = 'Vérifie ta connexion puis appuie sur Actualiser.'; el('lead-story').textContent = 'Les nouvelles seront affichées dès que le réseau sera disponible.'; }
    } finally { busy = false; el('refresh-news').disabled = false; }
  }
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  document.querySelectorAll('[data-topic]').forEach(button => button.addEventListener('click', () => { topic = button.dataset.topic; limit = 12; render(); }));
  el('translation-toggle').addEventListener('click', () => { french = !french; store.set('actuz-french', french); render(); });
  el('live-form').addEventListener('submit', event => event.preventDefault());
  ['live-query', 'live-language', 'live-source', 'live-period'].forEach(id => el(id).addEventListener(id === 'live-query' ? 'input' : 'change', () => { limit = 12; render(); }));
  el('reset-filters').addEventListener('click', resetFilters); el('refresh-news').addEventListener('click', refresh);
  el('load-more').addEventListener('click', () => { const firstNew = itemsForView()[limit]; limit += 12; render(); if (firstNew) document.getElementById('news-' + firstNew.id)?.querySelector('h3 a')?.focus({ preventScroll: true }); });
  el('daily-edition').addEventListener('change', () => { const url = new URL(location.href); url.search = ''; url.searchParams.set('view', 'daily'); url.searchParams.set('edition', el('daily-edition').value); history.pushState({}, '', url); loadEdition(el('daily-edition').value); });
  addEventListener('online', refresh); addEventListener('offline', () => { offline = true; renderHealth(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  addEventListener('popstate', () => { const u = new URL(location.href); const view = u.searchParams.has('date') ? 'archives' : u.searchParams.get('view') || 'live'; setView(['live', 'daily', 'saved', 'archives'].includes(view) ? view : 'live', false); if (view === 'daily' && u.searchParams.get('edition')) { el('daily-edition').value = u.searchParams.get('edition'); loadEdition(u.searchParams.get('edition')); } });
  setInterval(() => { if (!document.hidden) refresh(); }, 300000);
  setView(initial.searchParams.has('date') ? 'archives' : ['daily', 'saved', 'archives'].includes(initial.searchParams.get('view')) ? initial.searchParams.get('view') : 'live', false);
  refresh();
})();
