(function () {
  'use strict';
  var sdk = window.__CORTEX_PLUGIN_SDK__, registry = window.__CORTEX_PLUGINS__;
  if (!sdk || !registry) return;
  var h = sdk.React.createElement, useState = sdk.hooks.useState, useEffect = sdk.hooks.useEffect;
  var API = '/api/plugins/tosort';
  var labels = { running: 'Läuft', awaiting_review: 'Vorbereitung abgeschlossen · Freigabe ausstehend', failed: 'Fehlgeschlagen', not_measurable: 'nicht messbar' };
  var steps = { scan: 'Katalog', hash: 'Dublettenprüfung', registers: 'Register', learning: 'Lernabgleich', routing: 'Routing', review: 'Freigabetabelle' };
  function date(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT/.test(value)) return 'nicht messbar';
    var d = new Date(value);
    return Number.isFinite(d.getTime()) ? d.toLocaleString('de-DE') : 'nicht messbar';
  }
  function App() {
    var state = useState(null), data = state[0], setData = state[1];
    var action = useState(false), pending = action[0], setPending = action[1];
    var notice = useState(''), message = notice[0], setMessage = notice[1];
    useEffect(function () {
      var live = true;
      function refresh() {
        sdk.fetchJSON(API + '/status').then(function (value) { if (live) setData(value); })
          .catch(function () { if (live) setData(null); });
      }
      refresh();
      var timer = setInterval(refresh, 2500);
      return function () { live = false; clearInterval(timer); };
    }, []);
    function start() {
      setPending(true); setMessage('');
      sdk.fetchJSON(API + '/lauf', { method: 'POST', headers: { 'X-TOSORT-Action': 'start' } })
        .then(function (run) { setData(function (old) { return Object.assign({}, old, { run: run }); }); })
        .catch(function () { setMessage('Laufstart nicht verfügbar. Status erneut prüfen.'); })
        .finally(function () { setPending(false); });
    }
    var run = data && data.run || {};
    var cards = [['inbox', 'Eingang'], ['clarification', 'Klärung (Altbestand)'], ['review', 'Manuelle Prüfung']].map(function (entry) {
      var pool = data && data.pools && data.pools[entry[0]] || {};
      var measured = pool.status === 'measured' && Number.isSafeInteger(pool.count) && pool.count >= 0;
      var age = measured && Number.isFinite(pool.oldest_age_seconds) && pool.oldest_age_seconds >= 0;
      return h('article', { className: 'tosort-card', key: entry[0] },
        h('h2', null, entry[1]), h('p', { className: 'tosort-count' }, measured ? String(pool.count) : 'nicht messbar'),
        h('p', null, 'Älteste Datei: ', measured && pool.count === 0 ? 'keine Dateien' : age ? Math.floor(pool.oldest_age_seconds / 86400) + ' Tage' : 'nicht messbar'));
    });
    return h('main', { className: 'tosort-app' },
      h('h1', null, 'TOSORT'),
      h('p', null, 'Eingänge und Vorbereitung zur Freigabe'),
      h('div', { className: 'tosort-grid' }, cards),
      h('p', null, 'Dateialter nach letzter Änderung; keine Aussage zum Dokumentdatum.'),
      h('section', { className: 'tosort-card', 'aria-label': 'Laufstatus' },
        h('h2', null, 'Laufstatus'),
        h('p', { role: 'status', 'aria-live': 'polite' }, labels[run.status] || 'nicht messbar', steps[run.step] ? ' · ' + steps[run.step] : ''),
        h('p', null, 'Letzter Start: ', date(run.started_at)),
        h('p', null, 'Letztes Ende: ', date(run.finished_at)),
        h('p', null, 'Letzter Routing-Nachweis (Dateiänderung): ', date(data && data.last_routing_at)),
        h('p', null, 'Der Lauf erstellt Vorschläge und eine Freigabetabelle. Die Ablage erfolgt separat nach Freigabe.'),
        h('button', { type: 'button', disabled: pending || run.status === 'running' || !data || data.can_start !== true, onClick: start }, pending ? 'Start wird angefordert …' : 'TOSORT-Lauf starten'),
        data && data.can_start !== true ? h('p', null, 'Laufstart nicht aktiviert') : null,
        message ? h('p', { role: 'alert' }, message) : null));
  }
  registry.register('tosort', App);
})();
