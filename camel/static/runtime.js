// runtime.js

const signal = (initial) => {
  let value = initial;
  const subscribers = new Set();
  const set = (next) => { value = next; subscribers.forEach(fn => fn(next)); };
  return {
    get: () => value,
    set,
    subscribe(fn) { subscribers.add(fn); },
    restore: () => set(initial),
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
    case "Append": {
      const target = resolveStateRef(action.target, env);
      target.set([...target.get(), evalValue(action.value, env)]);
      return;
    }
    case "Restore": {
      const target = resolveStateRef(action.target, env);
      target.restore();
      return;
    }
    default:
      throw new Error(`don't know how to run action "${action.name}"`);
  }
};

const renderChildren = (children, env, vars, scopes) => children.map(child => render(child, env, vars, scopes));

const renderElement = (node, env, vars, scopes) => {
  const element = document.createElement(node.tag);
  element.append(...renderChildren(node.children, env, vars, scopes));

  if (node.classes.length) element.className = node.classes.join(" ");

  if (node.attributes.length) {
    const grouped = node.attributes.reduce((map, [name, value]) =>
      new Map(map).set(name, [...(map.get(name) ?? []), value]),
    new Map());

    grouped.forEach((values, name) => element.setAttribute(name, values.join(" ")));
  }

  node.events.forEach(event => {
    element.addEventListener(event.name, () => {
      event.actions.forEach(action => runAction(action, env));
    });
  });

  if (node.bind.type === "StateRef") {
    const stateRef = resolveStateRef(node.bind, env);
    element.value = stateRef.get();
    element.addEventListener("input", () => {
      stateRef.set(element.value);
    });
    stateRef.subscribe(next => {
      element.value = next;
    });
  }

  if (scopes.length) element.dataset.scope = scopes.join(" ");

  return element;
}

const renderFragment = (node, env, vars, scopes) => {
  const fragment = document.createDocumentFragment();
  fragment.append(...renderChildren(node.children, env, vars, scopes));
  return fragment;
}

const renderText = (node) => {
  return document.createTextNode(node.contents);
}

const renderRawHtml = (node) => {
  const tmpl = document.createElement("template");
  tmpl.innerHTML = node.contents;
  return tmpl.content;
}

const renderState = (node, env, vars, scopes) => {
  const childEnv = {
    ...env, ...Object.fromEntries(
      Object.entries(node.initial).map(([name, value]) => [name, signal(value)])
    )
  };
  return render(node.child, childEnv, vars, scopes);
}

const renderStateRef = (node, env, vars) => {
  const sig = resolveStateRef(node, env, vars);
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

const renderIf = (node, env, vars, scopes) => {
  const start = document.createComment("if");
  const end = document.createComment("/if");
  const fragment = document.createDocumentFragment();
  fragment.append(start, end);

  const update = () => {
    while (start.nextSibling !== end) {
      start.nextSibling.remove();
    }
    const branch = evalCondition(node.condition, env) ? node.then : node.otherwise;
    end.before(render(branch, env, vars, scopes));
  };

  update();
  conditionDependencies(node.condition, env).forEach(sig => sig.subscribe(update));
  return fragment;
};

const renderForEach = (node, env, vars, scopes) => {
  const start = document.createComment("each");
  const end = document.createComment("/each");
  const fragment = document.createDocumentFragment();
  fragment.append(start, end);

  const list = resolveStateRef(node.list, env);

  const update = () => {
    while (start.nextSibling !== end) {
      start.nextSibling.remove();
    }
    list.get().forEach(item => {
      end.before(render(node.body, env, { ...vars, [node.var]: item }, scopes));
    })
  }

  update();
  list.subscribe(update);
  return fragment;
}

const renderVarRef = (node, _env, vars) => {
  const value = vars[node.name];
  if (!value) throw new Error(`no such var: "${node.name}"`);
  return document.createTextNode(value);
}

const render = (node, env, vars, scopes = []) => {
  switch (node.type) {
    case "Elem":
      return renderElement(node, env, vars, scopes);
    case "Text":
      return renderText(node);
    case "RawHtml":
      return renderRawHtml(node);
    case "Fragment":
      return renderFragment(node, env, vars, scopes);
    case "Empty":
      return document.createDocumentFragment();
    case "State":
      return renderState(node, env, vars, scopes);
    case "StateRef":
      return renderStateRef(node, env, vars);
    case "If":
      return renderIf(node, env, vars, scopes);
    case "ForEach":
      return renderForEach(node, env, vars, scopes);
    case "VarRef":
      return renderVarRef(node, env, vars);
    case "StyleScope":
      return render(node.child, env, vars, [...scopes, node.id]);
    default:
      throw new Error(`don't know how to render node "${node.type}"`);
  }
}

const reRender = (doc) => {
  const root = document.getElementById("root");
  root.replaceChildren(render(doc, {}, {}, []));
}

const mount = () => {
  // Removes trailing backslash if present
  const page = site[window.location.pathname.replace(/\/$/, "") || "/"];
  reRender(page ?? site["/404"]);
}

document.addEventListener("DOMContentLoaded", mount);

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
    mount,
    reRender,
  };
}

