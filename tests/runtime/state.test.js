const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, resolveStateRef } = require("../../camel/static/runtime.js");

test("State creates a signal reachable by StateRef inside its child", () => {
  global.document = makeDocument();
  const node = render(
    {
      type: "State",
      initial: { clicks: 0 },
      child: { type: "StateRef", name: "clicks" },
    },
    {},
  );
  assert.strictEqual(node.text, "0");
});

test("StateRef renders the current value, not always zero", () => {
  global.document = makeDocument();
  const node = render(
    {
      type: "State",
      initial: { clicks: 7 },
      child: { type: "StateRef", name: "clicks" },
    },
    {},
  );
  assert.strictEqual(node.text, "7");
});

test("StateRef updates its text node when the signal changes", () => {
  global.document = makeDocument();
  const { signal } = require("../../camel/static/runtime.js");
  const clicks = signal(0);
  const node = render({ type: "StateRef", name: "clicks" }, { clicks });
  assert.strictEqual(node.text, "0");
  clicks.set(1);
  assert.strictEqual(node.text, "1");
});

test("State nests - an inner State shadows an outer one of the same name", () => {
  global.document = makeDocument();
  const node = render(
    {
      type: "State",
      initial: { x: "outer" },
      child: {
        type: "State",
        initial: { x: "inner" },
        child: { type: "StateRef", name: "x" },
      },
    },
    {},
  );
  assert.strictEqual(node.text, "inner");
});

test("StateRef to an undeclared name raises a clear error", () => {
  global.document = makeDocument();
  assert.throws(
    () => render({ type: "StateRef", name: "nope" }, {}),
    /no such state reference: "nope"/,
  );
});

test("resolveStateRef is the single place that error comes from", () => {
  global.document = makeDocument();
  assert.throws(
    () => resolveStateRef({ type: "StateRef", name: "nope" }, {}),
    /no such state reference: "nope"/,
  );
});
