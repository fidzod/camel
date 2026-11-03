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

test("mount renders the /404 page for a path with no matching page", () => {
  global.document = makeDocument();
  const doc = global.document;
  global.window = { location: { pathname: "/nope" } };
  global.site = {
    "/": { type: "Text", contents: "home" },
    "/404": { type: "Text", contents: "not found" },
  };

  mount();

  assert.strictEqual(doc._root.toString(), "<div>not found</div>");
});

test("mount strips a trailing slash before looking up the route", () => {
  global.document = makeDocument();
  const doc = global.document;
  global.window = { location: { pathname: "/about/" } };
  global.site = { "/about": { type: "Text", contents: "about" } };

  mount();

  assert.strictEqual(doc._root.toString(), "<div>about</div>");
});

test("mount treats a bare trailing-slash root the same as /", () => {
  global.document = makeDocument();
  const doc = global.document;
  global.window = { location: { pathname: "/" } };
  global.site = { "/": { type: "Text", contents: "home" } };

  mount();

  assert.strictEqual(doc._root.toString(), "<div>home</div>");
});
