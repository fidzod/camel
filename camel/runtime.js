const root = document.getElementById("root");

let state = {};
let reactiveStatements = {};
let statementId = 0;

const actions = {
    increment: (args) => {
        state[args[0][1]]++;
        updateReactiveNodes();
    },
};

function resolveCondition(cond) {
    const l = cond[1];
    let left =
        l[0] === "number" ? parseInt(l[1]) : l[0] === "text" ? l[1] : state[l[1]];

    const r = cond[2];
    let right =
        r[0] === "number" ? parseInt(r[1]) : r[0] === "text" ? r[1] : state[r[1]];

    if (cond[0] === "gt") return left > right;
    if (cond[0] === "gte") return left >= right;
    if (cond[0] === "lt") return left < right;
    if (cond[0] === "lte") return left <= right;
    if (cond[0] === "eq") return left === right;
}

function updateReactiveNodes() {
    document.querySelectorAll("[data-reactive]").forEach((node) => {
        const key = node.dataset.reactive;
        node.textContent = state[key];
    });
    document.querySelectorAll("[data-reactive-statement]").forEach((node) => {
        const elem = reactiveStatements[node.dataset.reactiveStatement];
        const result = resolveCondition(elem[1]);
        if (node.dataset.lastResult === String(result)) return;
        node.dataset.lastResult = String(result);
        const contents = elem[!result + 2];
        while (node.firstChild) node.removeChild(node.firstChild);
        node.appendChild(renderElement(contents));
    });
}

function renderElement(elem) {
    const type = elem[0];

    if (type === "text") {
        const text = elem[1];
        return document.createTextNode(text);
    }

    if (type === "stateRef") {
        const label = elem[1];
        const span = document.createElement("span");
        span.dataset.reactive = label;
        return span;
    }

    if (type === "if") {
        const span = document.createElement("span");
        const id = statementId++;
        reactiveStatements[id] = elem;
        span.dataset.reactiveStatement = id;
        return span;
    }

    // type is element

    const tag = elem[1],
        attrs = elem[2],
        children = elem[3];
    let e = document.createElement(tag);

    for (let child of children) e.appendChild(renderElement(child));

    for (let attr of attrs) {
        const attrType = attr[1],
            attrLabel = attr[0],
            attrValue = attr[2];

        if (attrType === "string") {
            e.setAttribute(attrLabel, attrValue);
        } else if (attrType === "action") {
            const action = attrValue[0],
                args = attrValue[1];
            e.addEventListener(attrLabel, () => {
                actions[action](args);
            });
        }
    }

    return e;
}

function renderRoute() {
    let loc = document.location.hash.split("#")[1] || "/";
    let page = site[loc] || site["/error404"];
    state = { ...page.state };
    while (root.firstChild) root.removeChild(root.firstChild);
    root.appendChild(renderElement(page.tree));
    updateReactiveNodes();
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("load", renderRoute);
