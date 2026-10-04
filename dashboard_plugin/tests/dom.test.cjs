const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const React = require('react');
const { createRoot } = require('react-dom/client');
const { act } = React;
const base = path.resolve(__dirname, '..');

test('Real React DOM: aggregate status, start, polling, failure, privacy', async () => {
  const dom = new JSDOM('<div id="root"></div>', { url: 'http://localhost/tosort', runScripts: 'outside-only' });
  global.window = dom.window; global.document = dom.window.document;
  global.IS_REACT_ACT_ENVIRONMENT = true;
  let App, poll, fail = false, posts = 0;
  let data = {can_start:true, pools:{inbox:{status:'measured',count:7,oldest_age_seconds:172800}},
    run:{status:'not_measurable'}, secret:'PATIENT_SECRET.pdf'};
  dom.window.setInterval = (fn) => { poll = fn; return 1; };
  dom.window.clearInterval = () => {};
  dom.window.__CORTEX_PLUGINS__ = {register:(name, component) => {assert.equal(name,'tosort'); App=component;}};
  dom.window.__CORTEX_PLUGIN_SDK__ = {React, hooks:React, fetchJSON:async (url, options) => {
    if(fail) throw new Error('PATIENT_SECRET');
    if(options?.method === 'POST') {posts++; assert.equal(options.headers['X-TOSORT-Action'],'start'); return {status:'running',step:'routing'};}
    return data;
  }};
  dom.window.eval(fs.readFileSync(path.join(base,'dist/index.js'),'utf8'));
  const root = createRoot(document.getElementById('root'));
  await act(async () => root.render(React.createElement(App)));
  const text = () => document.body.textContent;
  assert.match(text(),/7/); assert.match(text(),/2 Tage/); assert.match(text(),/nicht messbar/);
  assert.ok(!text().includes('SECRET'));
  fs.writeFileSync(path.join(base,'evidence/dom-fixture.html'),document.documentElement.outerHTML);
  await act(async () => document.querySelector('button').click());
  assert.equal(posts,1); assert.equal(document.querySelector('button').disabled,true);
  assert.match(document.querySelector('[role=status]').textContent,/Läuft · Routing/);
  data = {...data, run:{status:'awaiting_review'}};
  await act(async () => poll());
  assert.match(text(),/Freigabe ausstehend/); assert.equal(document.querySelector('button').disabled,false);
  fail = true;
  await act(async () => document.querySelector('button').click());
  assert.match(document.querySelector('[role=alert]').textContent,/nicht verfügbar/);
  assert.ok(!text().includes('SECRET'));
  await act(async () => poll());
  assert.equal(document.querySelector('button').disabled,true);
  assert.equal(document.querySelector('.tosort-count').textContent,'nicht messbar');
  await act(async () => root.unmount());
  dom.window.close();
});
