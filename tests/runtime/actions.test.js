const { test } = require("node:test");
const assert = require("node:assert");
const { makeDocument } = require("./dom-stub");

global.document = makeDocument();
const { render, signal, runAction } = require("../../camel/static/runtime.js");

const literal = value => ({ type: "Literal", value });
const ref = name => ({ type: "StateRef", name });

test("Add increments the target signal by amount", () => {
  const clicks = signal(1);
  runAction({ type: "Action", name: "Add", target: ref("clicks"), amount: literal(1) }, { clicks });
  assert.strictEqual(clicks.get(), 2);
});

test("Add's amount may itself be a StateRef", () => {
  const clicks = signal(1);
  const step = signal(5);
  runAction({ type: "Action", name: "Add", target: ref("clicks"), amount: ref("step") }, { clicks, step });
  assert.strictEqual(clicks.get(), 6);
});

test("Add against an undeclared target raises", () => {
  assert.throws(
    () => runAction({ type: "Action", name: "Add", target: ref("nope"), amount: literal(1) }, {}),
    /no such state reference: "nope"/,
  );
});

test("Append adds value to the end of the target list", () => {
  const tasks = signal(["milk"]);
  runAction({ type: "Action", name: "Append", target: ref("tasks"), value: literal("eggs") }, { tasks });
  assert.deepStrictEqual(tasks.get(), ["milk", "eggs"]);
});

test("Append's value may itself be a StateRef", () => {
  const tasks = signal(["milk"]);
  const next = signal("eggs");
  runAction({ type: "Action", name: "Append", target: ref("tasks"), value: ref("next") }, { tasks, next });
  assert.deepStrictEqual(tasks.get(), ["milk", "eggs"]);
});

test("Append against an undeclared target raises", () => {
  assert.throws(
    () => runAction({ type: "Action", name: "Append", target: ref("nope"), value: literal("eggs") }, {}),
    /no such state reference: "nope"/,
  );
});

test("an unknown action name raises", () => {
  assert.throws(
    () => runAction({ type: "Action", name: "Mystery" }, {}),
    /don't know how to run action "Mystery"/,
  );
});

test("clicking an Elem with on_click runs its actions", () => {
  global.document = makeDocument();
  const clicks = signal(0);
  const button = render(
    {
      type: "Elem",
      tag: "button",
      classes: [],
      children: [],
      events: [
        {
          name: "click",
          actions: [{ type: "Action", name: "Add", target: ref("clicks"), amount: literal(1) }],
        },
      ],
    },
    { clicks },
  );
  assert.strictEqual(clicks.get(), 0);
  button.dispatch("click");
  assert.strictEqual(clicks.get(), 1);
  button.dispatch("click");
  assert.strictEqual(clicks.get(), 2);
});

test("multiple actions on one event all run, in order", () => {
  global.document = makeDocument();
  const clicks = signal(0);
  const order = [];
  const trackingAction = (name) => ({
    type: "Action",
    name: "Add",
    target: ref("clicks"),
    amount: { type: "Literal", get value() { order.push(name); return 1; } },
  });
  const button = render(
    {
      type: "Elem",
      tag: "button",
      classes: [],
      children: [],
      events: [{ name: "click", actions: [trackingAction("first"), trackingAction("second")] }],
    },
    { clicks },
  );
  button.dispatch("click");
  assert.deepStrictEqual(order, ["first", "second"]);
  assert.strictEqual(clicks.get(), 2);
});
