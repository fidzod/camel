const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, signal } = require("../../camel/static/runtime.js");

const ref = name => ({ type: "StateRef", name });
const empty = { type: "Empty" };

function inputNode(bind = empty) {
  return { type: "Elem", tag: "input", classes: [], children: [], events: [], bind };
}

test("an unbound element has no value wiring", () => {
  global.document = makeDocument();
  const element = render(inputNode(), {}, {});
  assert.strictEqual(element.value, undefined);
});

test("bind sets the element's initial value from the current state", () => {
  global.document = makeDocument();
  const value = signal("hello");
  const element = render(inputNode(ref("value")), { value }, {});
  assert.strictEqual(element.value, "hello");
});

test("typing into the element (an input event) writes back to state", () => {
  global.document = makeDocument();
  const value = signal("");
  const element = render(inputNode(ref("value")), { value }, {});
  element.value = "typed";
  element.dispatch("input");
  assert.strictEqual(value.get(), "typed");
});

test("changing the state elsewhere updates the element's value", () => {
  global.document = makeDocument();
  const value = signal("");
  const element = render(inputNode(ref("value")), { value }, {});
  value.set("set from outside");
  assert.strictEqual(element.value, "set from outside");
});

test("bind against an undeclared state ref raises", () => {
  global.document = makeDocument();
  assert.throws(
    () => render(inputNode(ref("nope")), {}, {}),
    /no such state reference: "nope"/,
  );
});
