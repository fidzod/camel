const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { signal } = require("../../camel/static/runtime.js");

test("get returns the initial value before any set", () => {
  const s = signal(0);
  assert.strictEqual(s.get(), 0);
});

test("set updates the value seen by get", () => {
  const s = signal(0);
  s.set(5);
  assert.strictEqual(s.get(), 5);
});

test("subscribers are called with the new value on set", () => {
  const s = signal(0);
  const seen = [];
  s.subscribe(value => seen.push(value));
  s.set(1);
  s.set(2);
  assert.deepStrictEqual(seen, [1, 2]);
});

test("subscribing does not itself trigger the callback", () => {
  const s = signal(0);
  let calls = 0;
  s.subscribe(() => { calls += 1; });
  assert.strictEqual(calls, 0);
});

test("multiple subscribers all get notified", () => {
  const s = signal(0);
  const a = [];
  const b = [];
  s.subscribe(value => a.push(value));
  s.subscribe(value => b.push(value));
  s.set(9);
  assert.deepStrictEqual(a, [9]);
  assert.deepStrictEqual(b, [9]);
});

test("restore resets the value back to what the signal was created with", () => {
  const s = signal("seed");
  s.set("changed");
  s.restore();
  assert.strictEqual(s.get(), "seed");
});

test("restore notifies subscribers with the initial value", () => {
  const s = signal(0);
  const seen = [];
  s.subscribe(value => seen.push(value));
  s.set(1);
  s.restore();
  assert.deepStrictEqual(seen, [1, 0]);
});
