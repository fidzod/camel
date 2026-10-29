const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, signal } = require("../../camel/static/runtime.js");

const ref = name => ({ type: "StateRef", name });
const varRef = name => ({ type: "VarRef", name });

function li(varName = "item") {
  return {
    type: "Elem", tag: "li", classes: [], children: [varRef(varName)],
    events: [], bind: { type: "Empty" },
  };
}

function forEachNode({ list = "items", var: varName = "item", body = li(varName) } = {}) {
  return { type: "ForEach", list: ref(list), var: varName, body };
}

test("renders one element per item, in order", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["a", "b", "c"]);
  doc._root.append(render(forEachNode(), { items }));
  assert.strictEqual(
    doc._root.toString(),
    "<div><!--each--><li>a</li><li>b</li><li>c</li><!--/each--></div>",
  );
});

test("renders nothing between the markers for an empty list", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal([]);
  doc._root.append(render(forEachNode(), { items }));
  assert.strictEqual(doc._root.toString(), "<div><!--each--><!--/each--></div>");
});

test("re-renders when the list signal changes", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["a"]);
  doc._root.append(render(forEachNode(), { items }));
  assert.strictEqual(doc._root.toString(), "<div><!--each--><li>a</li><!--/each--></div>");

  items.set(["a", "b"]);
  assert.strictEqual(
    doc._root.toString(),
    "<div><!--each--><li>a</li><li>b</li><!--/each--></div>",
  );

  items.set([]);
  assert.strictEqual(doc._root.toString(), "<div><!--each--><!--/each--></div>");
});

test("a ForEach over an undeclared state ref raises", () => {
  global.document = makeDocument();
  assert.throws(
    () => render(forEachNode(), {}),
    /no such state reference: "items"/,
  );
});

test("VarRef to an undeclared var raises a clear error", () => {
  global.document = makeDocument();
  assert.throws(
    () => render(varRef("nope"), {}, {}),
    /no such var: "nope"/,
  );
});

test("vars threads through a nested Elem (regression: renderChildren used to drop it)", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["a"]);
  const ul = {
    type: "Elem", tag: "ul", classes: [], events: [],
    children: [forEachNode()], bind: { type: "Empty" },
  };
  doc._root.append(render(ul, { items }));
  assert.strictEqual(doc._root.toString(), "<div><ul><!--each--><li>a</li><!--/each--></ul></div>");
});

test("vars threads through a nested Fragment", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["a"]);
  const fragment = { type: "Fragment", children: [forEachNode()] };
  doc._root.append(render(fragment, { items }));
  assert.strictEqual(doc._root.toString(), "<div><!--each--><li>a</li><!--/each--></div>");
});

test("vars threads through a nested State", () => {
  global.document = makeDocument();
  const doc = global.document;
  const node = { type: "State", initial: { items: ["a"] }, child: forEachNode() };
  doc._root.append(render(node, {}));
  assert.strictEqual(doc._root.toString(), "<div><!--each--><li>a</li><!--/each--></div>");
});

test("vars threads through a nested If branch", () => {
  global.document = makeDocument();
  const doc = global.document;
  const items = signal(["a"]);
  const clicks = signal(1);
  const node = {
    type: "If",
    condition: { type: "Condition", op: "Eq", left: ref("clicks"), right: { type: "Literal", value: 1 } },
    then: forEachNode(),
    otherwise: { type: "Text", contents: "none" },
  };
  doc._root.append(render(node, { items, clicks }));
  assert.strictEqual(
    doc._root.toString(),
    "<div><!--if--><!--each--><li>a</li><!--/each--><!--/if--></div>",
  );
});

test("a nested ForEach using the same var name shadows the outer one, then restores it", () => {
  global.document = makeDocument();
  const doc = global.document;
  const outer = signal(["A", "B"]);
  const inner = signal(["1", "2"]);
  const node = forEachNode({
    list: "outer",
    var: "item",
    body: {
      type: "Fragment",
      children: [
        varRef("item"),
        forEachNode({ list: "inner", var: "item", body: varRef("item") }),
      ],
    },
  });
  doc._root.append(render(node, { outer, inner }));
  assert.strictEqual(
    doc._root.toString(),
    "<div><!--each-->A<!--each-->12<!--/each-->B<!--each-->12<!--/each--><!--/each--></div>",
  );
});
