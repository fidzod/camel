const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render } = require("../../camel/static/runtime.js");

test("renders Text", () => {
  global.document = makeDocument();
  const node = render({ type: "Text", contents: "hi" }, {});
  assert.strictEqual(node.text, "hi");
});

test("renders Elem with tag, classes, and children", () => {
  global.document = makeDocument();
  const node = render(
    {
      type: "Elem",
      tag: "div",
      classes: ["card", "featured"],
      children: [{ type: "Text", contents: "hi" }],
      events: [],
    },
    {},
  );
  assert.strictEqual(node.toString(), '<div class="card featured">hi</div>');
});

test("Elem with no classes gets no class attribute", () => {
  global.document = makeDocument();
  const node = render(
    { type: "Elem", tag: "p", classes: [], children: [], events: [] },
    {},
  );
  assert.strictEqual(node.toString(), "<p></p>");
});

test("Fragment flattens its children directly into the parent", () => {
  global.document = makeDocument();
  const doc = global.document;
  const fragmentNode = render(
    {
      type: "Fragment",
      children: [
        { type: "Text", contents: "a" },
        { type: "Text", contents: "b" },
      ],
    },
    {},
  );
  doc._root.append(fragmentNode);
  assert.strictEqual(doc._root.toString(), "<div>ab</div>");
});

test("unknown node type raises", () => {
  global.document = makeDocument();
  assert.throws(() => render({ type: "Nonsense" }, {}), /don't know how to render/);
});
