const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { mount, reRender } = require("../../camel/static/runtime.js");

test("reRender replaces root's contents with the rendered doc", () => {
  global.document = makeDocument();
  const doc = global.document;

  reRender({ type: "Text", contents: "first" });
  assert.strictEqual(doc._root.toString(), "<div>first</div>");

  reRender({ type: "Text", contents: "second" });
  assert.strictEqual(doc._root.toString(), "<div>second</div>");
});

test("mount renders the page matching the current path", () => {
  global.document = makeDocument();
  const doc = global.document;
  global.window = { location: { pathname: "/about" } };
  global.site = {
    "/": { type: "Text", contents: "home" },
    "/about": { type: "Text", contents: "about" },
  };

  mount();

  assert.strictEqual(doc._root.toString(), "<div>about</div>");
});

test("mount raises for a path with no matching page", () => {
  global.document = makeDocument();
  global.window = { location: { pathname: "/nope" } };
  global.site = { "/": { type: "Text", contents: "home" } };

  assert.throws(() => mount(), /404|not found/i);
});
