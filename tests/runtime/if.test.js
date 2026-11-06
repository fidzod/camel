const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, signal, evalValue, evalCondition, conditionDependencies } =
  require("../../camel/static/runtime.js");

const literal = value => ({ type: "Literal", value });
const ref = name => ({ type: "StateRef", name });

test("evalValue reads a Literal directly", () => {
  assert.strictEqual(evalValue(literal(1), {}), 1);
});

test("evalValue reads a StateRef's current value", () => {
  const clicks = signal(5);
  assert.strictEqual(evalValue(ref("clicks"), { clicks }), 5);
});

test("evalCondition Eq compares its operands", () => {
  const clicks = signal(1);
  const env = { clicks };
  assert.strictEqual(
    evalCondition({ type: "Condition", op: "Eq", left: ref("clicks"), right: literal(1) }, env),
    true,
  );
  assert.strictEqual(
    evalCondition({ type: "Condition", op: "Eq", left: ref("clicks"), right: literal(2) }, env),
    false,
  );
});

test("conditionDependencies finds the StateRef operand on either side", () => {
  const clicks = signal(1);
  const env = { clicks };
  const leftRef = conditionDependencies(
    { type: "Condition", op: "Eq", left: ref("clicks"), right: literal(1) },
    env,
  );
  const rightRef = conditionDependencies(
    { type: "Condition", op: "Eq", left: literal(1), right: ref("clicks") },
    env,
  );
  assert.deepStrictEqual(leftRef, [clicks]);
  assert.deepStrictEqual(rightRef, [clicks]);
});

test("conditionDependencies is empty when both sides are literals", () => {
  assert.deepStrictEqual(
    conditionDependencies({ type: "Condition", op: "Eq", left: literal(1), right: literal(1) }, {}),
    [],
  );
});

function ifNode(then, otherwise) {
  return {
    type: "If",
    condition: { type: "Condition", op: "Eq", left: ref("clicks"), right: literal(1) },
    then,
    otherwise,
  };
}

test("renders the then branch when the condition holds", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(1);
  doc._root.append(render(ifNode({ type: "Text", contents: "click" }, { type: "Text", contents: "clicks" }), { clicks }));
  assert.strictEqual(doc._root.toString(), "<div><!--if-->click<!--/if--></div>");
});

test("renders the otherwise branch when the condition doesn't hold", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(2);
  doc._root.append(render(ifNode({ type: "Text", contents: "click" }, { type: "Text", contents: "clicks" }), { clicks }));
  assert.strictEqual(doc._root.toString(), "<div><!--if-->clicks<!--/if--></div>");
});

test("swaps branches when the dependency changes", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(1);
  doc._root.append(render(ifNode({ type: "Text", contents: "click" }, { type: "Text", contents: "clicks" }), { clicks }));
  clicks.set(2);
  assert.strictEqual(doc._root.toString(), "<div><!--if-->clicks<!--/if--></div>");
  clicks.set(1);
  assert.strictEqual(doc._root.toString(), "<div><!--if-->click<!--/if--></div>");
});

test("swaps correctly when a branch renders to a Fragment, not a single node", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(1);
  const multi = {
    type: "Fragment",
    children: [{ type: "Text", contents: "A" }, { type: "Text", contents: "B" }],
  };
  doc._root.append(render(ifNode(multi, { type: "Text", contents: "single" }), { clicks }));
  assert.strictEqual(doc._root.toString(), "<div><!--if-->AB<!--/if--></div>");
  clicks.set(2);
  assert.strictEqual(doc._root.toString(), "<div><!--if-->single<!--/if--></div>");
  clicks.set(1);
  assert.strictEqual(doc._root.toString(), "<div><!--if-->AB<!--/if--></div>");
});

test("renders the default otherwise (Empty) as nothing when the condition doesn't hold", () => {
  global.document = makeDocument();
  const doc = global.document;
  const clicks = signal(2);
  doc._root.append(render(ifNode({ type: "Text", contents: "click" }, { type: "Empty" }), { clicks }));
  assert.strictEqual(doc._root.toString(), "<div><!--if--><!--/if--></div>");
});

test("a condition over an undeclared state ref raises", () => {
  global.document = makeDocument();
  assert.throws(
    () => render(ifNode({ type: "Text", contents: "x" }, { type: "Text", contents: "y" }), {}),
    /no such state reference: "clicks"/,
  );
});
