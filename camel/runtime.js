const root = document.getElementById("root");
let state = {};

const actions = {
    "increment": (key) => { state[key]++; updateReactiveNodes(); }
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

    const tag = elem[1], attrs = elem[2], children = elem[3];
    let e = document.createElement(tag);

    for (let child of children) e.appendChild(renderElement(child));

    for (let attr of attrs) {
        const attrType = attr[1], attrLabel = attr[0], attrValue = attr[2];

        if (attrType === "string") {
            e.setAttribute(attrLabel, attrValue);
        } else if (attrType === "action") {
            const action = attrValue[0], stateVar = attrValue[1];
            e.addEventListener(attrLabel, () => {
                actions[action](stateVar)
            });
        }
    }

    return e;
}

function renderRoute() {
    let loc = document.location.hash.split("#")[1] || "/";
    let page = site[loc] || site["/error404"];
    state = { ...page.state };
    while (root.firstChild) root.removeChild(root.firstChild)
    root.appendChild(renderElement(page.tree));
    updateReactiveNodes();
}

function updateReactiveNodes() {
    document.querySelectorAll('[data-reactive]').forEach(node => {
        const key = node.dataset.reactive;
        node.textContent = state[key];
    });
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("load", renderRoute);

