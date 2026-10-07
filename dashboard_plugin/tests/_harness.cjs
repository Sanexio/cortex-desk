'use strict';
// Shared mounting harness for the TOSORT dashboard component.
//
// The component is loaded with `require` instead of `window.eval` so V8
// attributes line and branch coverage to dist/index.js. Two consequences are
// handled here:
//
//  * the IIFE registers itself on execution, so the module cache entry is
//    dropped before every load to get a fresh registration per jsdom window;
//  * the module body runs in the Node realm, where a bare `setInterval` is the
//    Node global rather than `window.setInterval`. The polling timer is
//    therefore captured by swapping the Node globals for the short window in
//    which the component mounts or unmounts, and restoring them right after.
const assert = require('node:assert/strict');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const React = require('react');
const { createRoot } = require('react-dom/client');

const { act } = React;
const BASE = path.resolve(__dirname, '..');
const ENTRY = require.resolve(path.join(BASE, 'dist/index.js'));

function loadPlugin(dom) {
  global.window = dom.window;
  global.document = dom.window.document;
  global.IS_REACT_ACT_ENVIRONMENT = true;
  delete require.cache[ENTRY];
  require(ENTRY);
}

function newWindow() {
  return new JSDOM('<div id="root"></div>', {
    url: 'http://localhost/tosort',
    runScripts: 'outside-only',
  });
}

async function withTimers(stub, fn) {
  const realSetInterval = global.setInterval;
  const realClearInterval = global.clearInterval;
  global.setInterval = stub.setInterval;
  global.clearInterval = stub.clearInterval;
  try {
    return await fn();
  } finally {
    global.setInterval = realSetInterval;
    global.clearInterval = realClearInterval;
  }
}

/**
 * Mounts the registered component against a controllable fake SDK.
 *
 * @param {object} options
 * @param {object} options.status  payload returned by GET /status
 * @param {object} [options.sdk]   overrides merged into the fake SDK
 */
async function mount({ status, sdk: sdkOverrides = {} } = {}) {
  const dom = newWindow();
  let registered = null;
  let payload = status;
  let poll = null;
  let cleared = 0;
  const posts = [];

  const timers = {
    setInterval: (fn) => {
      poll = fn;
      return 1;
    },
    clearInterval: (handle) => {
      assert.equal(handle, 1, 'an unexpected interval handle was cleared');
      cleared += 1;
    },
  };
  Object.assign(dom.window, timers);

  dom.window.__CORTEX_PLUGINS__ = {
    register: (name, component) => {
      registered = { name, component };
    },
  };
  dom.window.__CORTEX_PLUGIN_SDK__ = Object.assign({
    React,
    hooks: React,
    fetchJSON: async (url, options) => {
      if (options && options.method === 'POST') {
        posts.push({ url, options });
        return { status: 'running', step: 'routing' };
      }
      return payload;
    },
  }, sdkOverrides);

  loadPlugin(dom);
  assert.ok(registered, 'component was not registered');
  assert.equal(registered.name, 'tosort');

  const root = createRoot(dom.window.document.getElementById('root'));
  await withTimers(timers, () =>
    act(async () => root.render(React.createElement(registered.component))));
  assert.ok(poll, 'the component did not register a polling interval');

  return {
    dom,
    posts,
    text: () => dom.window.document.body.textContent,
    query: (selector) => dom.window.document.querySelector(selector),
    cards: () => Array.from(dom.window.document.querySelectorAll('.tosort-card')),
    button: () => dom.window.document.querySelector('button'),
    click: async () => act(async () => dom.window.document.querySelector('button').click()),
    poll: async () => act(async () => poll()),
    // Fires the interval callback outside act(), for the unmounted case where
    // no re-render may happen any more.
    rawPoll: () => {
      poll();
      return new Promise((resolve) => setImmediate(resolve));
    },
    cleared: () => cleared,
    setStatus: (next) => {
      payload = next;
    },
    dispose: async () => {
      await withTimers(timers, () => act(async () => root.unmount()));
      dom.window.close();
    },
  };
}

module.exports = { BASE, ENTRY, mount, newWindow, loadPlugin, React, act };
