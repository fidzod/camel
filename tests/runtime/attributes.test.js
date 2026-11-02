const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render } = require("../../camel/static/runtime.js");

function elem(attributes) {
  return {
    type: "Elem", tag: "a", classes: [], children: [], events: [],
    bind: { type: "Empty" }, attributes,
  };
}

test("an Elem with no attributes gets none in the output", () => {
  global.document = makeDocument();
  const node = render(elem([]), {});
  assert.strictEqual(node.toString(), "<a></a>");
});

test("sets a single attribute", () => {
  global.document = makeDocument();
  const node = render(elem([["href", "https://example.com"]]), {});
  assert.strictEqual(node.toString(), '<a href="https://example.com"></a>');
});

test("sets multiple distinct attributes, in order", () => {
  global.document = makeDocument();
  const node = render(elem([["href", "/a"], ["target", "_blank"]]), {});
  assert.strictEqual(node.toString(), '<a href="/a" target="_blank"></a>');
});

test("the same attribute name repeated joins its values with a space", () => {
  global.document = makeDocument();
  const node = render(elem([["href", "/a"], ["href", "/b"]]), {});
  assert.strictEqual(node.toString(), '<a href="/a /b"></a>');
});
