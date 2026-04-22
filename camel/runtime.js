const root = document.getElementById("root");

let state = {};
let reactiveStatements = {};
let statementId = 0;

const actions = {
    increment: (args) => {
        state[args[0]]++;
        updateReactiveNodes();
    },
    append: (args) => {
        // n.b. append does not support hard coded values currently
        state[args[0]].push(state[args[1]]);
        updateReactiveNodes();
    },
    set: (args) => {
        state[args[0]] = args[1];
        updateReactiveNodes();
    },
    delete: (args) => {
        state[args[0]].splice(args[1], 1);
        updateReactiveNodes();
    },
    post: (args, vars) => {
        const url = args[0].map((a) => resolveArg(a, vars)).join("/");
        const pairs = args[1];
        const method = args.length > 2 ? args[2] : "POST";

        const data = Object.fromEntries(
            pairs.map(([key, value]) => [
                key,
                value[0] === "stateRef" ? state[value[1]] : resolveArg(value),
            ]),
        );

        fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        }).then(renderRoute);
    },
    refresh: () => {
        renderRoute();
    },
};

const operators = {
    gt: (l, r) => l > r,
    gte: (l, r) => l >= r,
    lt: (l, r) => l < r,
    lte: (l, r) => l <= r,
    eq: (l, r) => l === r,
};

const argResolvers = {
    varRef: (arg, vars) => arg[1].split(".").reduce((obj, key) => obj[key], vars),
    number: (arg) => parseInt(arg[1]),
    text: (arg) => arg[1],
    stateRef: (arg) => arg[1],
};

function resolveArg(arg, vars) {
    const resolver = argResolvers[arg[0]];
    return resolver ? resolver(arg, vars) : arg;
}

function applyCondition(cond) {
    return operators[cond[0]](resolveArg(cond[1]), resolveArg(cond[2]));
}

function updateTextNodes() {
    document.querySelectorAll("[data-reactive]").forEach((node) => {
        const key = node.dataset.reactive;
        node.textContent = state[key];
    });
}

function updateStatements() {
    document.querySelectorAll("[data-reactive-statement]").forEach((node) => {
        const elem = reactiveStatements[node.dataset.reactiveStatement];

        if (elem[0] === "if") {
            const result = applyCondition(elem[1]);
            if (node.dataset.lastResult === String(result)) return;
            node.dataset.lastResult = String(result);
            const contents = elem[!result + 2];
            while (node.firstChild) node.removeChild(node.firstChild);
            node.appendChild(render(contents));
        } else if (elem[0] === "each") {
            const list = state[elem[1][1]];
            const e = document.createDocumentFragment();
            for (let [i, item] of list.entries()) {
                const iterVars = { [elem[2]]: item, index: i };
                e.appendChild(render(elem[3], iterVars));
            }
            while (node.firstChild) node.removeChild(node.firstChild);
            node.appendChild(e);
        }
    });
}
function updateBindings() {
    document.querySelectorAll("[data-reactive-bind]").forEach((node) => {
        node.value = state[node.dataset.reactiveBind];
    });
}

function updateReactiveNodes() {
    updateTextNodes();
    updateStatements();
    updateBindings();
}

function renderText(elem, vars = {}) {
    const text = elem[1];
    return document.createTextNode(text);
}

function renderStateRef(elem, vars = {}) {
    const label = elem[1];
    const span = document.createElement("span");
    span.dataset.reactive = label;
    return span;
}

function renderVarRef(elem, vars = {}) {
    const label = elem[1];
    const span = document.createElement("span");
    const value = label.split(".").reduce((obj, key) => obj[key], vars);
    span.textContent = value;
    return span;
}

function renderIf(elem, vars = {}) {
    const span = document.createElement("span");
    const id = statementId++;
    reactiveStatements[id] = elem;
    span.dataset.reactiveStatement = id;
    return span;
}

function renderEach(elem, vars = {}) {
    const span = document.createElement("span");
    const id = statementId++;
    reactiveStatements[id] = elem;
    span.dataset.reactiveStatement = id;
    return span;
}

function applyStringAttr(e, label, value) {
    e.setAttribute(label, value);
}

function applyActionAttr(e, label, value, vars) {
    const actionList = value;
    e.addEventListener(label, () => {
        actionList.forEach(([actionName, actionArgs]) => {
            const resolved = actionArgs.map((a) => resolveArg(a, vars));
            actions[actionName](resolved, vars);
        });
    });
}

function applyBindAttr(e, value) {
    e.addEventListener("change", (e) => {
        state[value[1]] = e.target.value;
    });
    e.dataset.reactiveBind = value[1];
}

function applyAttr(e, attr, vars) {
    const [label, type, value] = attr;
    if (type === "string") applyStringAttr(e, label, value);
    else if (type === "action") applyActionAttr(e, label, value, vars);
    else if (type === "bind") applyBindAttr(e, value);
}

function renderElem(elem, vars = {}) {
    const [_, tag, attrs, children] = elem;
    let e = document.createElement(tag);

    for (let child of children) e.appendChild(render(child, vars));

    attrs.forEach((attr) => applyAttr(e, attr, vars));

    return e;
}

function render(elem, vars = {}) {
    const type = elem[0];

    if (type === "text") return renderText(elem, vars);
    if (type === "stateRef") return renderStateRef(elem, vars);
    if (type === "varRef") return renderVarRef(elem, vars);
    if (type === "if") return renderIf(elem, vars);
    if (type === "each") return renderEach(elem, vars);
    if (type === "elem") return renderElem(elem, vars);
}

function parseState() {
    Object.keys(state).forEach((key) => {
        let sv = state[key];
        if (Array.isArray(sv) && sv.length > 0 && sv[0] === "fetch") {
            fetch(sv[1])
                .then((r) => r.json())
                .then((data) => {
                    state[key] = data;
                    updateReactiveNodes();
                });
        }
    });
}

function renderRoute() {
    let loc = document.location.hash.split("#")[1] || "/";
    let page = site[loc] || site["/error404"];
    state = { ...page.state };
    parseState();
    while (root.firstChild) root.removeChild(root.firstChild);
    reactiveStatements = {};
    statementId = 0;
    root.appendChild(render(page.tree));
    updateReactiveNodes();
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("load", renderRoute);
