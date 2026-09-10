const vm = require('node:vm'), fs = require('node:fs'), assert = require('node:assert/strict');
function run(reduced) {
  const events = {}, animations = [], values = new Map();
  let observer;
  const element = (tagName = 'DIV') => ({tagName, style: {setProperty() {}}, classList: {toggle() {}, add() {}},
    setAttribute() {}, append() {}, prepend() {}, closest() {return null;},
    addEventListener(name, fn) {events[name] = fn;},
    animate() {const a = {cancelled: false, cancel() {this.cancelled = true;}, finished: new Promise(() => {})}; animations.push(a); return a;}
  });
  const button = element('BUTTON'), title = element('H2');
  const preference = {matches: reduced, addEventListener(name, fn) {this.change = fn;}};
  vm.runInNewContext(fs.readFileSync('js/tide-motion.js', 'utf8'), {
    document: {documentElement: element(), createElement: () => button,
      querySelector: selector => selector.startsWith('footer') ? element() : null,
      querySelectorAll: selector => selector.startsWith('main h2') ? [title] : []},
    matchMedia: query => query.includes('reduced') ? preference : {matches: false},
    localStorage: {getItem: key => values.get(key), setItem: (key, value) => values.set(key, value)},
    window: {IntersectionObserver: true},
    IntersectionObserver: class {constructor(fn) {observer = fn;} observe() {} unobserve() {}},
    setTimeout, requestAnimationFrame: fn => fn(), addEventListener() {}
  });
  observer([{isIntersecting: true, target: title}]);
  assert.equal(animations.length, reduced ? 0 : 1);
  if (!reduced) {
    events.click();
    assert.equal(values.get('gm-motion'), 'paused');
    assert.ok(animations[0].cancelled);
    events.click();
    assert.equal(values.get('gm-motion'), 'enabled');
    preference.matches = true; preference.change();
    observer([{isIntersecting: true, target: title}]);
    assert.equal(animations.length, 1);
  } else assert.equal(button.disabled, true);
}
run(false); run(true);
console.log('PASS: scroll entrances, pause cancellation, preference persistence, and live reduced-motion changes.');
