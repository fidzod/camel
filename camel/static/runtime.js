// runtime.js

const signal = (initial) => {
  let value = initial;
  const subscribers = new Set();
  return {
    get: () => value,
    set(next) { value = next; subscribers.forEach(fn => fn(next)); },
    subscribe(fn) { subscribers.add(fn); },
  }
}

const resolveStateRef = (stateRef, env) => {
  const sig = env[stateRef.name];
  if (!sig) throw new Error(`no such state reference: "${stateRef.name}"`);
  return sig;
}

const runAction = (action, env) => {
  switch (action.name) {
    case "Add": {
      const target = resolveStateRef(action.target, env);
      target.set(target.get() + evalValue(action.amount, env));
      return;
    }
    default:
      throw new Error(`don't know how to run action "${action.name}"`);
  }
};

const renderChildren = (children, env) => children.map(child => render(child, env));

const renderElement = (node, env) => {
  const element = document.createElement(node.tag);
  element.append(...renderChildren(node.children, env));
  if (node.classes.length) element.className = node.classes.join(" ");
  node.events.forEach(event => {
    element.addEventListener(event.name, () => {
      event.actions.forEach(action => runAction(action, env));
    });
  });
  return element;
}

const renderFragment = (node, env) => {
  const fragment = document.createDocumentFragment();
  fragment.append(...renderChildren(node.children, env));
  return fragment;
}

const renderText = (node, _env) => {
  return document.createTextNode(node.contents);
}

const renderState = (node, env) => {
  const childEnv = {
    ...env, ...Object.fromEntries(
      Object.entries(node.initial).map(([name, value]) => [name, signal(value)])
    )
  };
  return render(node.child, childEnv);
}

const renderStateRef = (node, env) => {
  const sig = resolveStateRef(node, env);
  const text = document.createTextNode(String(sig.get()));
  sig.subscribe(value => { text.textContent = String(value); });
  return text;
}

const evalValue = (value, env) => {
  switch (value.type) {
    case "Literal": return value.value;
    case "StateRef": {
      const sig = resolveStateRef(value, env);
      return sig.get();
    }
    default: throw new Error(`don't know how to evaluate value "${value.type}"`);
  }
};

const evalCondition = (condition, env) => {
  const left = evalValue(condition.left, env);
  const right = evalValue(condition.right, env);
  switch (condition.op) {
    case "Eq": return left === right;
    default: throw new Error(`don't know how to evaluate condition "${condition.op}"`);
  }
};

const conditionDependencies = (condition, env) =>
  [condition.left, condition.right]
    .filter(value => value.type === "StateRef")
    .map(value => resolveStateRef(value, env));

const renderIf = (node, env) => {
  const start = document.createComment("if");
  const end = document.createComment("/if");
  const fragment = document.createDocumentFragment();
  fragment.append(start, end);

  const update = () => {
    while (start.nextSibling !== end) {
      start.nextSibling.remove();
    }
    const branch = evalCondition(node.condition, env) ? node.then : node.otherwise;
    end.before(render(branch, env));
  };

  update();
  conditionDependencies(node.condition, env).forEach(sig => sig.subscribe(update));
  return fragment;
};

const render = (node, env) => {
  switch (node.type) {
    case "Elem":
      return renderElement(node, env);
    case "Text":
      return renderText(node, env);
    case "Fragment":
      return renderFragment(node, env);
    case "State":
      return renderState(node, env);
    case "StateRef":
      return renderStateRef(node, env);
    case "If":
      return renderIf(node, env);
    default:
      throw new Error(`don't know how to render node "${node.type}"`);
  }
}

// Exposed for testing in Node (see tests/runtime/) - inert in the browser,
// since `module` is never declared there and `typeof` is safe on it.
if (typeof module !== "undefined") {
  module.exports = {
    signal,
    resolveStateRef,
    runAction,
    render,
    evalValue,
    evalCondition,
    conditionDependencies,
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("root");
  root.append(render(site, {}));
});
