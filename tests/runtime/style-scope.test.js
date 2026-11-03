const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, signal } = require("../../camel/static/runtime.js");

const elem = (tag, children = []) => ({
  type: "Elem", tag, classes: [], events: [], bind: { type: "Empty" }, attributes: [], children,
});

const text = contents => ({ type: "Text", contents });

const scope = (id, child) => ({ type: "StyleScope", id, child });

test("an element outside any scope has no data-scope attribute", () => {
  global.document = makeDocument();
  const node = render(elem("p"), {}, {}, []);
  assert.strictEqual(node.dataset.scope, undefined);
});

test("elements inside a scope are stamped with its id", () => {
  global.document = makeDocument();
  const doc = global.document;
  doc._root.append(render(scope("abc", elem("p")), {}, {}, []));
  assert.strictEqual(doc._root.toString(), '<div><p data-scope="abc"></p></div>');
});

test("stamping reaches elements nested several levels deep in the scope", () => {
  global.document = makeDocument();
  const doc = global.document;
  const tree = scope("abc", elem("div", [elem("ul", [elem("li", [text("x")])])]));
  doc._root.append(render(tree, {}, {}, []));
  assert.strictEqual(
    doc._root.toString(),
    '<div><div data-scope="abc"><ul data-scope="abc"><li data-scope="abc">x</li></ul></div></div>',
  );
});

test("nested scopes accumulate - an element gets both ids, space-separated", () => {
  global.document = makeDocument();
  const doc = global.document;
  const tree = scope("outer", elem("div", [scope("inner", elem("p"))]));
  doc._root.append(render(tree, {}, {}, []));
  assert.strictEqual(
    doc._root.toString(),
    '<div><div data-scope="outer"><p data-scope="outer inner"></p></div></div>',
  );
});

test("sibling scopes don't leak into each other", () => {
  global.document = makeDocument();
  const doc = global.document;
  const tree = {
    type: "Fragment",
    children: [scope("a", elem("p")), scope("b", elem("span"))],
  };
  doc._root.append(render(tree, {}, {}, []));
  assert.strictEqual(
    doc._root.toString(),
    '<div><p data-scope="a"></p><span data-scope="b"></span></div>',
  );
});

test("a scope wrapping an If still stamps whichever branch renders", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(1);
  const tree = scope("abc", {
    type: "If",
    condition: { type: "Condition", op: "Eq", left: { type: "StateRef", name: "clicks" }, right: { type: "Literal", value: 1 } },
    then: elem("p"),
    otherwise: elem("span"),
  });
  doc._root.append(render(tree, { clicks }, {}, []));
  assert.strictEqual(
    doc._root.toString(),
    '<div><!--if--><p data-scope="abc"></p><!--/if--></div>',
  );
});

test("a scope wrapping a ForEach stamps every rendered item, including after a re-render", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["x"]);
  const tree = scope("abc", {
    type: "ForEach",
    list: { type: "StateRef", name: "items" },
    var: "item",
    body: elem("li", [{ type: "VarRef", name: "item" }]),
  });
  doc._root.append(render(tree, { items }, {}, []));
  assert.strictEqual(
    doc._root.toString(),
    '<div><!--each--><li data-scope="abc">x</li><!--/each--></div>',
  );

  items.set(["x", "y"]);
  assert.strictEqual(
    doc._root.toString(),
    '<div><!--each--><li data-scope="abc">x</li><li data-scope="abc">y</li><!--/each--></div>',
  );
});
