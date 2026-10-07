'use strict';
// Branch coverage for the render rules in src/index.js.
//
// dom.test.cjs covers the end-to-end interaction path (mount, start, poll,
// failure). This file pins the per-field fallbacks that the privacy contract
// in README.md depends on: anything that is not a known, well-formed value
// must render as "nicht messbar" and must never reach the DOM verbatim.
const { test } = require('node:test');
const assert = require('node:assert/strict');

const { mount, newWindow, loadPlugin } = require('./_harness.cjs');

const SECRET = 'PATIENT_SECRET.pdf';

function pools(overrides) {
  return Object.assign({
    inbox: { status: 'measured', count: 0, oldest_age_seconds: null },
    clarification: { status: 'measured', count: 0, oldest_age_seconds: null },
    review: { status: 'measured', count: 0, oldest_age_seconds: null },
  }, overrides);
}

function statusPayload(overrides) {
  return Object.assign({
    can_start: true,
    pools: pools(),
    last_routing_at: null,
    run: { status: 'not_measurable', step: null, started_at: null, finished_at: null },
  }, overrides);
}

test('missing host SDK or registry leaves the page untouched', () => {
  for (const globals of [{}, { __CORTEX_PLUGIN_SDK__: {} }, { __CORTEX_PLUGINS__: {} }]) {
    const dom = newWindow();
    let registered = 0;
    if (globals.__CORTEX_PLUGINS__) {
      dom.window.__CORTEX_PLUGINS__ = { register: () => { registered += 1; } };
    }
    if (globals.__CORTEX_PLUGIN_SDK__) {
      dom.window.__CORTEX_PLUGIN_SDK__ = {};
    }
    assert.doesNotThrow(() => loadPlugin(dom));
    assert.equal(registered, 0);
    assert.equal(dom.window.document.getElementById('root').childNodes.length, 0);
    dom.window.close();
  }
});

test('all three pools are rendered with their labels', async () => {
  const view = await mount({ status: statusPayload() });
  const headings = view.cards().map((card) => card.querySelector('h2').textContent);
  assert.deepEqual(headings,
    ['Eingang', 'Klärung (Altbestand)', 'Manuelle Prüfung', 'Laufstatus']);
  await view.dispose();
});

test('an empty measured pool shows zero and "keine Dateien"', async () => {
  const view = await mount({ status: statusPayload() });
  const card = view.cards()[0];
  assert.equal(card.querySelector('.tosort-count').textContent, '0');
  assert.match(card.textContent, /Älteste Datei: keine Dateien/);
  await view.dispose();
});

test('a measured pool without a usable age keeps the count but not the age', async () => {
  const view = await mount({
    status: statusPayload({
      pools: pools({ inbox: { status: 'measured', count: 4, oldest_age_seconds: null } }),
    }),
  });
  const card = view.cards()[0];
  assert.equal(card.querySelector('.tosort-count').textContent, '4');
  assert.match(card.textContent, /Älteste Datei: nicht messbar/);
  await view.dispose();
});

test('negative and non-integer counts are rejected, not rounded', async () => {
  for (const count of [-1, 1.5, '7', null, undefined, Number.NaN, 2 ** 53]) {
    const view = await mount({
      status: statusPayload({
        pools: pools({ inbox: { status: 'measured', count, oldest_age_seconds: 86400 } }),
      }),
    });
    const card = view.cards()[0];
    assert.equal(card.querySelector('.tosort-count').textContent, 'nicht messbar',
      'count ' + String(count) + ' must not be displayed');
    assert.match(card.textContent, /Älteste Datei: nicht messbar/);
    await view.dispose();
  }
});

test('a pool that is not measured is never shown as a number', async () => {
  for (const status of ['not_measurable', 'measured ', 'MEASURED', undefined, SECRET]) {
    const view = await mount({
      status: statusPayload({
        pools: pools({ inbox: { status, count: 12, oldest_age_seconds: 86400 } }),
      }),
    });
    assert.equal(view.cards()[0].querySelector('.tosort-count').textContent, 'nicht messbar');
    assert.ok(!view.text().includes('12'));
    assert.ok(!view.text().includes('SECRET'));
    await view.dispose();
  }
});

test('a negative age is rejected and a positive one is floored to whole days', async () => {
  const cases = [[-1, 'nicht messbar'], [0, '0 Tage'], [86399, '0 Tage'],
    [86400, '1 Tage'], [259199, '2 Tage']];
  for (const [age, expected] of cases) {
    const view = await mount({
      status: statusPayload({
        pools: pools({ inbox: { status: 'measured', count: 3, oldest_age_seconds: age } }),
      }),
    });
    assert.match(view.cards()[0].textContent, new RegExp('Älteste Datei: ' + expected));
    await view.dispose();
  }
});

test('well-formed timestamps are rendered as localised dates', async () => {
  const view = await mount({
    status: statusPayload({
      last_routing_at: '2026-04-15T08:30:00+00:00',
      run: { status: 'awaiting_review', step: 'review',
        started_at: '2026-04-15T08:00:00+00:00', finished_at: '2026-04-15T08:31:00+00:00' },
    }),
  });
  const text = view.text();
  for (const label of ['Letzter Start', 'Letztes Ende', 'Letzter Routing-Nachweis']) {
    assert.ok(text.includes(label));
  }
  // Formatted, not echoed: no raw ISO string, but the date is present.
  assert.ok(!text.includes('2026-04-15T08:00:00+00:00'));
  assert.equal((text.match(/\d{1,2}\.\d{1,2}\.2026/g) || []).length, 3);
  assert.ok(!text.includes('nicht messbar'));
  await view.dispose();
});

test('malformed timestamps fall back to "nicht messbar"', async () => {
  // '2026-02-30T…' is deliberately absent: JS rolls that over to 2026-03-02.
  const broken = ['2026-13-45T00:00:00Z', '2026-00-10T00:00:00Z', '0000-00-00T00:00:00Z',
    '15.04.2026', '2026-04-15', '', 'nicht messbar'];
  for (const value of broken) {
    const view = await mount({
      status: statusPayload({
        last_routing_at: value,
        run: { status: 'awaiting_review', step: null, started_at: value, finished_at: value },
      }),
    });
    assert.equal((view.text().match(/nicht messbar/g) || []).length, 3,
      'timestamp ' + JSON.stringify(value) + ' must not be rendered');
    await view.dispose();
  }
});

test('non-string timestamps fall back to "nicht messbar"', async () => {
  for (const value of [0, 1776240000, null, true, { iso: '2026-04-15T08:00:00Z' },
    ['2026-04-15T08:00:00Z']]) {
    const view = await mount({
      status: statusPayload({
        last_routing_at: value,
        run: { status: 'awaiting_review', step: null, started_at: value, finished_at: value },
      }),
    });
    assert.equal((view.text().match(/nicht messbar/g) || []).length, 3);
    assert.ok(!view.text().includes('2026'));
    await view.dispose();
  }
});

test('every known run step is rendered with its own label', async () => {
  const expected = { scan: 'Katalog', hash: 'Dublettenprüfung', registers: 'Register',
    learning: 'Lernabgleich', routing: 'Routing', review: 'Freigabetabelle' };
  for (const [step, label] of Object.entries(expected)) {
    const view = await mount({
      status: statusPayload({
        run: { status: 'running', step, started_at: null, finished_at: null },
      }),
    });
    assert.equal(view.query('[role=status]').textContent, 'Läuft · ' + label);
    await view.dispose();
  }
});

test('unknown run statuses and steps are not echoed into the DOM', async () => {
  const cases = [{ status: SECRET, step: SECRET }, { status: 'constructor', step: 'constructor' },
    { status: 'toString', step: 'toString' }, { status: '__proto__', step: '__proto__' },
    { status: '', step: '' }, { status: 42, step: 42 }];
  for (const run of cases) {
    const view = await mount({
      status: statusPayload({
        run: Object.assign({ started_at: null, finished_at: null }, run),
      }),
    });
    assert.equal(view.query('[role=status]').textContent, 'nicht messbar',
      'run ' + JSON.stringify(run) + ' must not reach the DOM');
    assert.ok(!view.text().includes('SECRET'));
    await view.dispose();
  }
});

test('a locked run start disables the button and names the reason', async () => {
  for (const canStart of [false, null, undefined, 1, 'true']) {
    const view = await mount({ status: statusPayload({ can_start: canStart }) });
    assert.equal(view.button().disabled, true);
    assert.match(view.text(), /Laufstart nicht aktiviert/);
    await view.click();
    assert.equal(view.posts.length, 0, 'a disabled button must not post');
    await view.dispose();
  }
});

test('an enabled run start offers the button without the lock notice', async () => {
  const view = await mount({ status: statusPayload() });
  assert.equal(view.button().disabled, false);
  assert.ok(!view.text().includes('Laufstart nicht aktiviert'));
  assert.equal(view.button().textContent, 'TOSORT-Lauf starten');
  await view.dispose();
});

test('a running state blocks a second start even while can_start is true', async () => {
  const view = await mount({
    status: statusPayload({
      run: { status: 'running', step: 'scan', started_at: null, finished_at: null },
    }),
  });
  assert.equal(view.button().disabled, true);
  await view.click();
  assert.equal(view.posts.length, 0);
  await view.dispose();
});

test('a status payload without pools or run degrades instead of throwing', async () => {
  for (const payload of [{}, { can_start: true }, { pools: null, run: null, can_start: true },
    { pools: 'x', run: 'y', can_start: true }]) {
    const view = await mount({ status: payload });
    assert.equal(view.cards().length, 4);
    for (const card of view.cards().slice(0, 3)) {
      assert.equal(card.querySelector('.tosort-count').textContent, 'nicht messbar');
    }
    assert.equal(view.query('[role=status]').textContent, 'nicht messbar');
    await view.dispose();
  }
});

test('the start request carries the action header and no body', async () => {
  const view = await mount({ status: statusPayload() });
  await view.click();
  assert.equal(view.posts.length, 1);
  const { url, options } = view.posts[0];
  assert.equal(url, '/api/plugins/tosort/lauf');
  assert.equal(options.method, 'POST');
  assert.equal(options.headers['X-TOSORT-Action'], 'start');
  assert.equal(options.body, undefined);
  await view.dispose();
});

test('a failing status poll clears the aggregates instead of keeping stale ones', async () => {
  let broken = false;
  const view = await mount({
    status: statusPayload(),
    sdk: {
      fetchJSON: async () => {
        if (broken) throw new Error(SECRET);
        return statusPayload({
          pools: pools({ inbox: { status: 'measured', count: 9, oldest_age_seconds: 0 } }),
        });
      },
    },
  });
  assert.equal(view.cards()[0].querySelector('.tosort-count').textContent, '9');
  broken = true;
  await view.poll();
  assert.equal(view.cards()[0].querySelector('.tosort-count').textContent, 'nicht messbar');
  assert.equal(view.button().disabled, true, 'no start without a known status');
  assert.ok(!view.text().includes('SECRET'));
  await view.dispose();
});

test('a failing start shows a neutral notice and never the error text', async () => {
  const view = await mount({
    status: statusPayload(),
    sdk: {
      fetchJSON: async (url, options) => {
        if (options && options.method === 'POST') throw new Error(SECRET);
        return statusPayload();
      },
    },
  });
  assert.equal(view.query('[role=alert]'), null);
  await view.click();
  assert.match(view.query('[role=alert]').textContent,
    /Laufstart nicht verfügbar\. Status erneut prüfen\./);
  assert.ok(!view.text().includes('SECRET'));
  // The button is released again so the operator can retry.
  assert.equal(view.button().disabled, false);
  assert.equal(view.button().textContent, 'TOSORT-Lauf starten');
  await view.dispose();
});

test('a successful start updates the run block without dropping the pools', async () => {
  const view = await mount({
    status: statusPayload({
      pools: pools({ inbox: { status: 'measured', count: 5, oldest_age_seconds: 0 } }),
    }),
  });
  await view.click();
  assert.equal(view.query('[role=status]').textContent, 'Läuft · Routing');
  assert.equal(view.cards()[0].querySelector('.tosort-count').textContent, '5');
  assert.equal(view.button().disabled, true);
  await view.dispose();
});

test('unmount clears the interval and silences a late response', async () => {
  let calls = 0;
  const view = await mount({
    status: statusPayload(),
    sdk: { fetchJSON: async () => { calls += 1; return statusPayload(); } },
  });
  assert.equal(calls, 1, 'the first status is fetched on mount');
  await view.poll();
  assert.equal(calls, 2);
  assert.equal(view.cleared(), 0);

  const root = view.dom.window.document.getElementById('root');
  await view.dispose();
  assert.equal(view.cleared(), 1, 'the polling interval must be cleared on unmount');
  assert.equal(root.childNodes.length, 0);

  // A response that arrives after unmount must be dropped, not applied.
  await view.rawPoll();
  assert.equal(calls, 3);
  assert.equal(root.childNodes.length, 0);
});
