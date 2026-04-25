const root = document.getElementById("root");
let state = {};
let reactiveStatements = {};
let statementId = 0;

function renderText(atom) {
    if (!atom.value) throw new TypeError("Malformed Text atom");
    return document.createTextNode(atom.value);
}

function applyAttributes(element, attributes) {
    Object.entries(attributes).forEach(([k, v]) => element.setAttribute(k, v));
}

function setState(arg, value) {
    state[arg.label].value = value;
}

function wrap(value) {
    if (typeof value === "string") return { type: "Text", value };
    if (typeof value === "number") return { type: "Number", value };
    if (Array.isArray(value)) return { type: "List", value };
    return value;
}

const actions = {
    increment: (args) => setState(args[0], Primitive(args[0]) + 1),
    set: (args) => setState(args[0], Primitive(args[1])),
    push: (args) => Primitive(args[0]).push(wrap(Primitive(args[1]))),
    remove: (args) => Primitive(args[0]).splice(args[1], 1),
    delete: (args) => {
        const url = args.map((a) => (a.type === undefined ? a : a.value)).join("/");
        fetch(url, {
            method: "DELETE",
        }).then(renderRoute);
    },
    post: (args) => {
        const urlLen = Primitive(args.pop());
        const url = args.slice(0, urlLen).map(Primitive).join("/");
        const body = args.slice(urlLen);
        const data = Object.fromEntries(
            body.map((l) => [Primitive(l.value[0]), Primitive(l.value[1])]),
        );
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        }).then(renderRoute);
    },
};

function resolveVars(arg, vars) {
    if (arg.type !== "VarRef") return arg;
    return arg.label.split(".").reduce((obj, key) => obj[key], vars);
}

function applyEventListeners(element, events, vars) {
    events.forEach((ev) =>
        element.addEventListener(ev.name, () =>
            ev.actions.forEach((action) => {
                if (actions[action.name] === undefined)
                    throw new TypeError(`Unknown action '${action.name}'`);
                actions[action.name](action.arguments.map((a) => resolveVars(a, vars)));
                updateReactiveNodes();
            }),
        ),
    );
}

function applyBinding(element, bindVar) {
    element.addEventListener("change", (e) => {
        state[bindVar.label].value = e.target.value;
        updateReactiveNodes();
    });
    element.dataset.reactiveBind = bindVar.label;
}

function renderElement(atom, vars) {
    if (!atom.tag || !Array.isArray(atom.children))
        throw new TypeError("Malformed Element atom");
    const element = document.createElement(atom.tag);
    element.className = atom.classes;
    atom.children.forEach((c) => element.appendChild(renderAtom(c, vars)));
    applyAttributes(element, atom.attributes);
    applyEventListeners(element, atom.events, vars);
    if (atom.boundTo !== null) applyBinding(element, atom.boundTo);
    return element;
}

function renderStateRef(atom) {
    if (!atom.label) throw new TypeError("Malformed StateRef atom");
    const span = document.createElement("span");
    span.dataset.reactive = atom.label;
    return span;
}

function renderVarRef(atom, vars) {
    if (!atom.label) throw new TypeError("Malformed VarRef atom");
    const value = atom.label.split(".").reduce((obj, key) => obj[key], vars);
    if (value === undefined)
        throw new TypeError(`No such var ${atom.label} is in scope.`);
    const span = document.createElement("span");
    span.textContent = value.value !== undefined ? value.value : value;
    return span;
}

function renderReactiveStatement(statement) {
    const span = document.createElement("span");
    const id = statementId++;
    reactiveStatements[id] = statement;
    span.dataset.reactiveStatement = id;
    return span;
}

function renderAtom(atom, vars = {}) {
    if (atom.type === "Text") return renderText(atom);
    if (atom.type === "Number") return renderText(atom);
    if (atom.type === "Element") return renderElement(atom, vars);
    if (atom.type === "StateRef") return renderStateRef(atom);
    if (atom.type === "VarRef") return renderVarRef(atom, vars);
    if (atom.type === "If") return renderReactiveStatement(atom);
    if (atom.type === "ForEach") return renderReactiveStatement(atom);

    if (!atom.type) throw new TypeError("Malformed atom");
    throw new TypeError(`Invalid atom type: ${atom.type}`);
}

function parseState() {
    Object.keys(state).forEach((key) => {
        if (state[key].type !== "Fetch") return;
        fetch(state[key].url)
            .then((r) => r.json())
            .then((data) => {
                state[key] = wrap(data);
                updateReactiveNodes();
            });
    });
}

function updateTextNodes() {
    document
        .querySelectorAll("[data-reactive]")
        .forEach((s) => (s.textContent = state[s.dataset.reactive].value));
}

function Primitive(p) {
    return p.type === "StateRef" ? state[p.label].value : p.value;
}

const conditions = {
    eq: (x, y) => x == y,
    gt: (x, y) => x > y,
    gte: (x, y) => x >= y,
    lt: (x, y) => x < y,
    lte: (x, y) => x <= y,
};

function applyCondition(condition) {
    return conditions[condition.name](
        Primitive(condition.x),
        Primitive(condition.y),
    );
}

function updateIf(statement, node) {
    const result = applyCondition(statement.condition);
    if (node.dataset.lastResult === String(result)) return;
    node.dataset.lastResult = String(result);
    while (node.firstChild) node.removeChild(node.firstChild);
    if (result) node.appendChild(renderAtom(statement.consequent));
    else if (statement.alternate !== null) {
        node.appendChild(renderAtom(statement.alternate));
    }
}

function updateForEach(statement, node) {
    const list =
        statement.list.type === "List"
            ? statement.list.value
            : state[statement.list.label].value;
    const body = document.createDocumentFragment();
    if (list === undefined) return;
    for (let [i, item] of list.entries()) {
        const iterVars = { [statement.var]: item, index: i };
        body.appendChild(renderAtom(statement.body, iterVars));
    }
    while (node.firstChild) node.removeChild(node.firstChild);
    node.appendChild(body);
}

function updateStatements() {
    document.querySelectorAll("[data-reactive-statement]").forEach((n) => {
        const statement = reactiveStatements[n.dataset.reactiveStatement];
        if (statement.type === "If") updateIf(statement, n);
        if (statement.type === "ForEach") updateForEach(statement, n);
    });
}

function updateBindings() {
    document.querySelectorAll("[data-reactive-bind]").forEach((n) => {
        n.value = state[n.dataset.reactiveBind].value;
    });
}

function updateReactiveNodes() {
    updateTextNodes();
    updateStatements();
    updateBindings();
}

function renderRoute() {
    reactiveStatements = {};
    statementId = 0;
    let loc = document.location.hash.split("#")[1] || "/";
    let page = site[loc] || site["/error404"];
    state = { ...page.state };
    parseState();
    while (root.firstChild) root.removeChild(root.firstChild);
    page.tree.forEach((a) => root.appendChild(renderAtom(a)));
    updateReactiveNodes();
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("load", renderRoute);
